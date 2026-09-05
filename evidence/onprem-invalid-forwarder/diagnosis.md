# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `onprem-invalid-azure-dns-forwarder`

Evidence completeness: 100.0%

## Observed path

- Source: branch-erp
- FQDN: `erpfiles.file.core.windows.net`
- Resolved IP: `None`
- Endpoint IP: `10.50.4.7`
- Effective next hop: `VirtualNetworkGateway`

## Findings

### PE-RESOLVER-001 · confirmed

An external DNS server attempts to forward directly to Azure's virtual DNS address.

- Evidence: `source_kind=on-premises`
- Evidence: `forward_to=168.63.129.16`
- Remediation: Forward the private namespace to an Azure DNS Private Resolver inbound endpoint reachable over VPN or ExpressRoute.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
