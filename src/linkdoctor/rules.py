from __future__ import annotations

import ipaddress
from typing import Any

from .models import Finding
from .zones import expected_zone, record_name


DNS_GUIDE = "https://learn.microsoft.com/troubleshoot/azure/private-link/troubleshoot-private-endpoint-dns-resolution"
CONNECT_GUIDE = "https://learn.microsoft.com/troubleshoot/azure/private-link/troubleshoot-private-endpoint-connectivity-failure"


def _finding(rule_id: str, status: str, confidence: str, severity: str, summary: str,
             evidence: list[str], remediation: str, reference: str) -> Finding:
    return Finding(rule_id, status, confidence, severity, summary, evidence, remediation, [reference])


def _is_private(value: str | None) -> bool:
    if not value:
        return False
    try:
        return ipaddress.ip_address(value).is_private
    except ValueError:
        return False


def diagnose(bundle: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    target = bundle.get("target", {})
    endpoint = bundle.get("private_endpoint", {})
    dns = bundle.get("dns_observation", {})
    private_dns = bundle.get("private_dns", {})
    resolver = bundle.get("resolver", {})
    route = bundle.get("routing", {})
    nsg = bundle.get("network_security", {})
    firewall = bundle.get("service_firewall", {})
    source = bundle.get("source", {})
    fqdn = target.get("fqdn", "")
    expected = expected_zone(fqdn)
    endpoint_ip = endpoint.get("private_ip")
    resolved_ip = dns.get("resolved_ip")

    connection = str(endpoint.get("connection_status", "unknown")).lower()
    provisioning = str(endpoint.get("provisioning_state", "unknown")).lower()
    if connection != "approved" or provisioning != "succeeded":
        findings.append(_finding(
            "PE-CONN-001", "root-cause", "confirmed", "critical",
            "The private endpoint is not both approved and successfully provisioned.",
            [f"connection_status={connection}", f"provisioning_state={provisioning}"],
            "Approve or recreate the endpoint connection and wait for successful provisioning before testing DNS.", CONNECT_GUIDE,
        ))

    zones = {str(item.get("name", "")).lower(): item for item in private_dns.get("zones", [])}
    zone = zones.get(expected or "")
    if expected and not zone:
        findings.append(_finding(
            "PE-DNS-001", "root-cause", "confirmed", "high",
            "The expected Azure Private DNS zone is absent from the evidence bundle.",
            [f"fqdn={fqdn}", f"expected_zone={expected}"],
            "Create or discover the expected zone, then associate it through a private endpoint DNS zone group.", DNS_GUIDE,
        ))
    if zone:
        records = {str(item.get("name", "")).lower(): item.get("ip") for item in zone.get("a_records", [])}
        actual_record = records.get(record_name(fqdn))
        if not actual_record or (endpoint_ip and actual_record != endpoint_ip):
            findings.append(_finding(
                "PE-DNS-002", "root-cause", "confirmed", "high",
                "The Private DNS A record is missing or does not match the endpoint IP.",
                [f"record={record_name(fqdn)}", f"record_ip={actual_record}", f"endpoint_ip={endpoint_ip}"],
                "Use a DNS zone group to create and maintain the record, then validate the resulting IP.", DNS_GUIDE,
            ))
        source_vnet = str(source.get("vnet_id", "")).lower()
        links = {str(item).lower() for item in zone.get("linked_vnets", [])}
        if source_vnet and source_vnet not in links:
            findings.append(_finding(
                "PE-DNS-003", "root-cause", "confirmed", "high",
                "The Private DNS zone is not linked to the querying virtual network.",
                [f"source_vnet={source_vnet}", f"linked_vnets={len(links)}"],
                "Add a non-registration VNet link or provide the namespace through an approved centralized DNS path.", DNS_GUIDE,
            ))

    result = str(dns.get("result", "unknown")).lower()
    if result == "resolved" and resolved_ip and not _is_private(resolved_ip):
        findings.append(_finding(
            "PE-DNS-004", "root-cause", "confirmed", "high",
            "The service FQDN resolves to a public address instead of the endpoint private IP.",
            [f"resolved_ip={resolved_ip}", f"endpoint_ip={endpoint_ip}"],
            "Correct the Private DNS zone, record and resolution path before investigating routing.", DNS_GUIDE,
        ))
    if result == "nxdomain" and zone:
        findings.append(_finding(
            "PE-DNS-005", "root-cause", "probable", "high",
            "A linked private namespace returns NXDOMAIN, consistent with a missing record or namespace interception.",
            [f"zone={expected}", "dns_result=nxdomain"],
            "Restore the required A record; evaluate NXDOMAIN fallback only when public resolution is intentionally required.", DNS_GUIDE,
        ))

    if source.get("kind") in {"on-premises", "cross-cloud"} and resolver.get("forward_to") == "168.63.129.16":
        findings.append(_finding(
            "PE-RESOLVER-001", "root-cause", "confirmed", "high",
            "An external DNS server attempts to forward directly to Azure's virtual DNS address.",
            [f"source_kind={source.get('kind')}", "forward_to=168.63.129.16"],
            "Forward the private namespace to an Azure DNS Private Resolver inbound endpoint reachable over VPN or ExpressRoute.", DNS_GUIDE,
        ))
    if resolver.get("required", False) and not resolver.get("ruleset_linked_to_source_vnet", False):
        findings.append(_finding(
            "PE-RESOLVER-002", "root-cause", "confirmed", "high",
            "The required DNS forwarding ruleset is not linked to the querying VNet.",
            ["ruleset_linked_to_source_vnet=false"],
            "Link the ruleset to the client VNet and retest recursive resolution.", DNS_GUIDE,
        ))

    if route.get("expected_next_hop") and route.get("actual_next_hop") != route.get("expected_next_hop"):
        findings.append(_finding(
            "PE-ROUTE-001", "root-cause", "confirmed", "high",
            "The effective next hop differs from the declared network path.",
            [f"expected={route.get('expected_next_hop')}", f"actual={route.get('actual_next_hop')}", f"prefix={route.get('matched_prefix')}"],
            "Review longest-prefix-match behavior, private endpoint network policies and the intended NVA/firewall path.", CONNECT_GUIDE,
        ))
    if str(nsg.get("decision", "unknown")).lower() == "deny":
        findings.append(_finding(
            "PE-NSG-001", "root-cause", "confirmed", "critical",
            "The effective network security decision denies the declared flow.",
            [f"rule={nsg.get('rule')}", f"port={target.get('port')}", f"protocol={target.get('protocol', 'TCP')}"],
            "Create the narrowest reviewed allow rule and verify the effective NSG result from the source interface.", CONNECT_GUIDE,
        ))
    if str(firewall.get("private_access", "unknown")).lower() == "deny":
        findings.append(_finding(
            "PE-SVC-001", "root-cause", "confirmed", "critical",
            "The target service access policy rejects the private endpoint path.",
            [f"private_access={firewall.get('private_access')}", f"public_access={firewall.get('public_access')}"],
            "Approve the endpoint connection and align the service network-access policy with the intended private path.", CONNECT_GUIDE,
        ))
    return findings
