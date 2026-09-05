from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Finding:
    rule_id: str
    status: str
    confidence: str
    severity: str
    summary: str
    evidence: list[str]
    remediation: str
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
