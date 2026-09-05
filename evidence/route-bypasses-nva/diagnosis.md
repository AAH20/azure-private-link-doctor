# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `endpoint-route-bypasses-central-nva`

Evidence completeness: 100.0%

## Observed path

- Source: regulated-app
- FQDN: `audit.blob.core.windows.net`
- Resolved IP: `10.80.2.10`
- Endpoint IP: `10.80.2.10`
- Effective next hop: `InterfaceEndpoint`

## Findings

### PE-ROUTE-001 · confirmed

The effective next hop differs from the declared network path.

- Evidence: `expected=VirtualAppliance`
- Evidence: `actual=InterfaceEndpoint`
- Evidence: `prefix=10.80.2.10/32`
- Remediation: Review longest-prefix-match behavior, private endpoint network policies and the intended NVA/firewall path.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
