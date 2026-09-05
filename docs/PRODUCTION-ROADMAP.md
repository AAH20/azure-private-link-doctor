# Production roadmap

## 0.1 — deterministic offline core (implemented)

- Versioned evidence format
- Six reproducible failure fixtures
- DNS, resolver, route, NSG, and service checks
- Sanitized support bundle and evidence receipt
- Terraform/Bicep remediation scaffolds
- Tests, container, CLI, and GitHub Action

## 0.2 — Azure read-only collectors

- Azure Resource Graph inventory adapter
- Private DNS zone, record, and VNet-link collector
- DNS Private Resolver ruleset/link collector
- Effective route and NSG collector
- Network Watcher connection diagnostics adapter
- Managed identity and least-privilege role definition

## 0.3 — enterprise operations

- Versioned JSON Schema and backward-compatibility tests
- OpenTelemetry traces and diagnostic metrics
- Signed evidence manifests and configurable retention
- SARIF output and ticketing/webhook integrations
- Multi-subscription and Azure Lighthouse operation

## 1.0 — controlled remediation

- Terraform plan and Azure deployment what-if gates
- Azure Policy and OPA/Conftest checks
- Approval, maintenance-window, rollback, and post-change verification workflow
- Rule evaluation benchmark with labeled incidents
- Published precision, recall, latency, and cost-per-diagnosis results

No autonomous write access should be introduced merely to make the demo appear more advanced. Production maturity is demonstrated by controlled authority, evidence, evaluation, and rollback.
