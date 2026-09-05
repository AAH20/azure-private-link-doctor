# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `keyvault-effective-nsg-deny`

Evidence completeness: 100.0%

## Observed path

- Source: deployment-agent
- FQDN: `secrets.vault.azure.net`
- Resolved IP: `10.70.2.9`
- Endpoint IP: `10.70.2.9`
- Effective next hop: `InterfaceEndpoint`

## Findings

### PE-NSG-001 · confirmed

The effective network security decision denies the declared flow.

- Evidence: `rule=DenyAllOutbound`
- Evidence: `port=443`
- Evidence: `protocol=TCP`
- Remediation: Create the narrowest reviewed allow rule and verify the effective NSG result from the source interface.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
