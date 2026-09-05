# LinkDoctor diagnosis

**Status: DIAGNOSED**

Scenario: `postgres-missing-record-nxdomain`

Evidence completeness: 100.0%

## Observed path

- Source: orders-api
- FQDN: `orders-db.postgres.database.azure.com`
- Resolved IP: `None`
- Endpoint IP: `10.40.3.5`
- Effective next hop: `InterfaceEndpoint`

## Findings

### PE-DNS-002 · confirmed

The Private DNS A record is missing or does not match the endpoint IP.

- Evidence: `record=orders-db`
- Evidence: `record_ip=None`
- Evidence: `endpoint_ip=10.40.3.5`
- Remediation: Use a DNS zone group to create and maintain the record, then validate the resulting IP.

### PE-DNS-005 · probable

A linked private namespace returns NXDOMAIN, consistent with a missing record or namespace interception.

- Evidence: `zone=privatelink.postgres.database.azure.com`
- Evidence: `dns_result=nxdomain`
- Remediation: Restore the required A record; evaluate NXDOMAIN fallback only when public resolution is intentionally required.

> The result is limited to supplied evidence; it does not prove end-to-end connectivity or authorize remediation.
