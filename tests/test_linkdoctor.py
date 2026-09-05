from __future__ import annotations

import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from linkdoctor.engine import analyze
from linkdoctor.render import write_outputs
from linkdoctor.zones import expected_zone


ROOT = Path(__file__).resolve().parents[1]


def fixture(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class LinkDoctorTests(unittest.TestCase):
    def assert_rule(self, file_name: str, rule_id: str):
        report = analyze(fixture(file_name))
        self.assertEqual(report["status"], "DIAGNOSED")
        self.assertIn(rule_id, {item["rule_id"] for item in report["findings"]})
        self.assertEqual(report["summary"]["evidence_completeness_percent"], 100)

    def test_zone_mapping_uses_longest_suffix(self):
        self.assertEqual(expected_zone("orders-db.postgres.database.azure.com"), "privatelink.postgres.database.azure.com")

    def test_missing_vnet_link_and_public_resolution(self):
        report = analyze(fixture("missing-vnet-link.json"))
        rules = {item["rule_id"] for item in report["findings"]}
        self.assertTrue({"PE-DNS-003", "PE-DNS-004"}.issubset(rules))

    def test_postgres_nxdomain(self):
        report = analyze(fixture("postgres-nxdomain.json"))
        rules = {item["rule_id"] for item in report["findings"]}
        self.assertTrue({"PE-DNS-002", "PE-DNS-005"}.issubset(rules))

    def test_onprem_invalid_forwarder(self):
        self.assert_rule("onprem-invalid-forwarder.json", "PE-RESOLVER-001")

    def test_unlinked_resolver_ruleset(self):
        self.assert_rule("resolver-ruleset-unlinked.json", "PE-RESOLVER-002")

    def test_nsg_deny(self):
        self.assert_rule("nsg-deny.json", "PE-NSG-001")

    def test_route_bypass(self):
        self.assert_rule("route-bypasses-nva.json", "PE-ROUTE-001")

    def test_healthy_evidence_has_no_diagnosis(self):
        bundle = fixture("nsg-deny.json")
        bundle["network_security"] = {"decision": "allow", "rule": "AllowHTTPS"}
        report = analyze(bundle)
        self.assertEqual(report["status"], "HEALTHY")
        self.assertEqual(report["findings"], [])

    def test_missing_evidence_is_incomplete(self):
        bundle = fixture("nsg-deny.json")
        del bundle["routing"]
        report = analyze(bundle)
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertIn("routing", report["summary"]["missing_sections"])

    def test_support_bundle_redacts_secret_and_subscription_guid(self):
        bundle = fixture("nsg-deny.json")
        bundle["secret"] = "do-not-export"
        bundle["source"]["vnet_id"] = "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/rg/providers/Microsoft.Network/virtualNetworks/vnet"
        report = analyze(bundle)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_outputs(bundle, report, directory)
            with zipfile.ZipFile(paths["support_bundle"]) as archive:
                sanitized = archive.read("sanitized-evidence.json").decode()
            self.assertNotIn("do-not-export", sanitized)
            self.assertNotIn("11111111-2222-3333-4444-555555555555", sanitized)

    def test_outputs_include_diagram_and_remediation(self):
        bundle = fixture("missing-vnet-link.json")
        report = analyze(bundle)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_outputs(bundle, report, directory)
            self.assertTrue(all(path.exists() for path in paths.values()))
            self.assertIn("azurerm_private_dns_zone_virtual_network_link", paths["terraform"].read_text())
            self.assertIn("flowchart LR", paths["diagram"].read_text())

    def test_receipt_is_stable_except_timestamp(self):
        bundle = fixture("route-bypasses-nva.json")
        first = analyze(bundle)
        second = analyze(copy.deepcopy(bundle))
        self.assertEqual(first["receipt"], second["receipt"])


if __name__ == "__main__":
    unittest.main()
