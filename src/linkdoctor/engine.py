from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .rules import diagnose
from .schema import REQUIRED_SECTIONS, validate_bundle


def analyze(bundle: dict[str, Any]) -> dict[str, Any]:
    missing = validate_bundle(bundle)
    findings = [] if missing else diagnose(bundle)
    present = len(REQUIRED_SECTIONS - set(missing))
    completeness = round(100 * present / len(REQUIRED_SECTIONS), 2)
    status = "INCOMPLETE" if missing else ("DIAGNOSED" if findings else "HEALTHY")
    report = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_id": bundle.get("scenario_id", "unknown"),
        "evidence_class": bundle.get("evidence_class", "declared"),
        "status": status,
        "summary": {
            "root_causes": len(findings),
            "confirmed": sum(f.confidence == "confirmed" for f in findings),
            "probable": sum(f.confidence == "probable" for f in findings),
            "evidence_completeness_percent": completeness,
            "missing_sections": missing,
        },
        "path": {
            "source": bundle.get("source", {}).get("name", "unknown"),
            "fqdn": bundle.get("target", {}).get("fqdn", "unknown"),
            "resolved_ip": bundle.get("dns_observation", {}).get("resolved_ip"),
            "endpoint_ip": bundle.get("private_endpoint", {}).get("private_ip"),
            "next_hop": bundle.get("routing", {}).get("actual_next_hop"),
        },
        "findings": [finding.to_dict() for finding in findings],
        "claim_boundary": "The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.",
    }
    stable = json.dumps({key: value for key, value in report.items() if key != "generated_at"}, sort_keys=True, separators=(",", ":")).encode()
    report["receipt"] = {"algorithm": "sha256", "content_digest": hashlib.sha256(stable).hexdigest()}
    return report
