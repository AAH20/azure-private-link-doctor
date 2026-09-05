# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `storage-missing-vnet-link`

Evidence completeness: 100.0%

## Observed path

- Source: checkout-vm
- FQDN: `orders.blob.core.windows.net`
- Resolved IP: `20.60.10.4`
- Endpoint IP: `10.40.2.4`
- Effective next hop: `InterfaceEndpoint`

## Findings

### PE-DNS-003 · confirmed

The Private DNS zone is not linked to the querying virtual network.

- Evidence: `source_vnet=/subscriptions/demo/resourcegroups/network/providers/microsoft.network/virtualnetworks/spoke-prod`
- Evidence: `linked_vnets=0`
- Remediation: Add a non-registration VNet link or provide the namespace through an approved centralized DNS path.

### PE-DNS-004 · confirmed

The service FQDN resolves to a public address instead of the endpoint private IP.

- Evidence: `resolved_ip=20.60.10.4`
- Evidence: `endpoint_ip=10.40.2.4`
- Remediation: Correct the Private DNS zone, record and resolution path before investigating routing.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
