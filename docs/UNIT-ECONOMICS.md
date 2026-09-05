# Unit economics

These are transparent planning assumptions, not promised savings. Replace every input with measured customer data before quoting ROI.

## Base case per incident

| Input | Manual workflow | With repeatable evidence workflow |
|---|---:|---:|
| Network engineer | 4.0 h | 1.0 h |
| Cloud/platform engineer | 3.0 h | 0.75 h |
| Security engineer | 1.5 h | 0.5 h |
| Blended loaded rate | $120/h | $120/h |
| Engineering cost | $1,020 | $270 |
| Avoided engineering cost |  | **$750/incident** |

If a customer has 12 relevant incidents per month, the modeled labor benefit is `$750 × 12 = $9,000/month`. If release delay costs $2,000 per hour and the workflow shortens one critical incident by three hours, the additional avoided delay is $6,000. Do not add that amount unless the customer can substantiate the cost of delay.

## Delivery model

| Offer | Indicative scope | Indicative price |
|---|---|---:|
| Diagnostic workshop | One topology, evidence contract, two incidents | $2,500–$5,000 |
| Production integration | Collectors, CI, dashboards, runbooks, policy alignment | $15,000–$40,000 |
| Managed reliability retainer | Rule maintenance, incident review, monthly KPI report | $3,000–$10,000/month |

Cloud consumption is customer-specific. The offline engine itself requires only CI or container compute. Live collection may introduce Log Analytics, Network Watcher, storage, automation, and egress costs; estimate these from the customer's region, retention, event volume, and execution frequency.

## KPIs

- Median and P90 mean time to diagnose
- First-pass root-cause precision confirmed by an engineer
- Evidence completeness rate
- Repeat incident rate by finding ID
- Change failure and rollback rates for approved remediations
- Escalations resolved without multi-team meetings
- Engineering hours and release-delay hours avoided
- False-positive and false-negative rates per rule/version

The strongest commercial proof is a before/after pilot with timestamped incidents, blinded engineer adjudication, and the same workload mix—not an unverified percentage claim.
