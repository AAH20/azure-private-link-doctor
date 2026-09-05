from __future__ import annotations

from typing import Any


REQUIRED_SECTIONS = {
    "source",
    "target",
    "private_endpoint",
    "dns_observation",
    "private_dns",
    "routing",
    "network_security",
    "service_firewall",
}


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED_SECTIONS - bundle.keys())
    if not isinstance(bundle.get("scenario_id", ""), str) or not bundle.get("scenario_id"):
        missing.append("scenario_id")
    return missing
