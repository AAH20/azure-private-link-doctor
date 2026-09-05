# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `resolver-ruleset-wrong-spoke`

Evidence completeness: 100.0%

## Observed path

- Source: analytics-vm
- FQDN: `warehouse.database.windows.net`
- Resolved IP: `None`
- Endpoint IP: `10.60.2.8`
- Effective next hop: `VirtualNetworkPeering`

## Findings

### PE-RESOLVER-002 · confirmed

The required DNS forwarding ruleset is not linked to the querying VNet.

- Evidence: `ruleset_linked_to_source_vnet=false`
- Remediation: Link the ruleset to the client VNet and retest recursive resolution.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
