# Security and evidence handling

Do not submit tenant exports, credentials, access tokens, customer names, internal hostnames, public IP inventories, or incident data to a public issue.

The support-bundle writer redacts keys whose names contain `secret`, `token`, `password`, `key`, or `connection_string`, and replaces subscription-shaped GUIDs. This is defense in depth, not a guarantee: operators must inspect every bundle before sharing it.

The tool is read-only. Generated Terraform and Bicep are review scaffolds and must pass peer review, policy checks, plan/what-if analysis, approval, and controlled deployment before use.

Report a suspected vulnerability privately to the repository owner through GitHub Security Advisories. Include the affected version, reproduction steps, impact, and a minimal sanitized example.
