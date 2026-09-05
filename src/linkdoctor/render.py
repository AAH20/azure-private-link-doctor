from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# LinkDoctor diagnosis", "",
        f"**Status: {report['status']}**", "",
        f"Scenario: `{report['scenario_id']}`", "",
        f"Evidence completeness: {summary['evidence_completeness_percent']}%", "",
        "## Observed path", "",
        f"- Source: {report['path']['source']}",
        f"- FQDN: `{report['path']['fqdn']}`",
        f"- Resolved IP: `{report['path']['resolved_ip']}`",
        f"- Endpoint IP: `{report['path']['endpoint_ip']}`",
        f"- Effective next hop: `{report['path']['next_hop']}`", "",
        "## Findings", "",
    ]
    if not report["findings"]:
        lines.append("- No root cause was identified from the supplied evidence.")
    for finding in report["findings"]:
        lines.extend([
            f"### {finding['rule_id']} · {finding['confidence']}", "",
            finding["summary"], "",
            *[f"- Evidence: `{item}`" for item in finding["evidence"]],
            f"- Remediation: {finding['remediation']}", "",
        ])
    if summary["missing_sections"]:
        lines.extend(["## Missing evidence", "", *[f"- `{item}`" for item in summary["missing_sections"]], ""])
    lines.extend([f"> {report['claim_boundary']}", ""])
    return "\n".join(lines)


def mermaid(report: dict[str, Any]) -> str:
    status = "Failure found" if report["findings"] else report["status"].title()
    return "\n".join([
        "flowchart LR",
        f"  SRC[\"{report['path']['source']}\"] --> DNS[\"DNS: {report['path']['resolved_ip']}\"]",
        f"  DNS --> PE[\"Private endpoint: {report['path']['endpoint_ip']}\"]",
        f"  PE --> HOP[\"Next hop: {report['path']['next_hop']}\"]",
        f"  HOP --> RESULT[\"{status}\"]",
        "",
    ])


def remediation(report: dict[str, Any]) -> tuple[str, str, str]:
    rules = {finding["rule_id"] for finding in report["findings"]}
    tf = ["# Review-only remediation scaffold. Do not apply without a plan and approval.", ""]
    bicep = ["// Review-only remediation scaffold. Supply verified resource IDs before deployment", "targetScope = 'resourceGroup'", ""]
    notes = ["# Remediation plan", "", "Generated suggestions require architecture review and post-change testing.", ""]
    if "PE-DNS-003" in rules:
        tf.extend([
            'variable "private_dns_zone_name" { type = string }',
            'variable "private_dns_zone_resource_group" { type = string }',
            'variable "source_vnet_id" { type = string }',
            'resource "azurerm_private_dns_zone_virtual_network_link" "reviewed" {',
            '  name                  = "link-reviewed-source-vnet"',
            '  resource_group_name   = var.private_dns_zone_resource_group',
            '  private_dns_zone_name = var.private_dns_zone_name',
            '  virtual_network_id    = var.source_vnet_id',
            '  registration_enabled  = false',
            '}', "",
        ])
        bicep.extend([
            "param privateDnsZoneName string", "param sourceVnetId string",
            "resource zone 'Microsoft.Network/privateDnsZones@2024-06-01' existing = { name: privateDnsZoneName }",
            "resource link 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {",
            "  parent: zone", "  name: 'link-reviewed-source-vnet'",
            "  location: 'global'", "  properties: { registrationEnabled: false, virtualNetwork: { id: sourceVnetId } }", "}", "",
        ])
        notes.append("- Add a non-registration VNet link after verifying the source VNet and centralized DNS architecture.")
    if "PE-DNS-002" in rules:
        notes.append("- Prefer a private endpoint DNS zone group so Azure maintains the endpoint A record.")
    if "PE-NSG-001" in rules:
        notes.append("- Derive the narrowest NSG allow rule from the verified source prefix, destination IP, protocol and port.")
    if "PE-ROUTE-001" in rules:
        notes.append("- Validate private endpoint network policies and longest-prefix-match behavior before changing a route table.")
    if len(notes) == 4:
        notes.append("- No automated remediation scaffold is safe for the diagnosed condition.")
    return "\n".join(tf), "\n".join(bicep), "\n".join(notes) + "\n"


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if key.lower() in {"secret", "token", "password", "key", "connection_string"} else _sanitize(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"/subscriptions/[0-9a-fA-F-]{36}", "/subscriptions/[REDACTED]", value)
    return value


def write_outputs(bundle: dict[str, Any], report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    tf, bicep, notes = remediation(report)
    paths = {
        "json": root / "diagnosis.json",
        "markdown": root / "diagnosis.md",
        "diagram": root / "network-path.mmd",
        "terraform": root / "remediation" / "main.tf",
        "bicep": root / "remediation" / "main.bicep",
        "remediation": root / "remediation" / "README.md",
        "support_bundle": root / "support-bundle.zip",
    }
    paths["terraform"].parent.mkdir(parents=True, exist_ok=True)
    paths["json"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    paths["markdown"].write_text(markdown(report), encoding="utf-8")
    paths["diagram"].write_text(mermaid(report), encoding="utf-8")
    paths["terraform"].write_text(tf, encoding="utf-8")
    paths["bicep"].write_text(bicep, encoding="utf-8")
    paths["remediation"].write_text(notes, encoding="utf-8")
    with zipfile.ZipFile(paths["support_bundle"], "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sanitized-evidence.json", json.dumps(_sanitize(bundle), indent=2) + "\n")
        archive.writestr("diagnosis.json", json.dumps(report, indent=2) + "\n")
        archive.writestr("diagnosis.md", markdown(report))
    return paths
