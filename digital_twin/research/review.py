from __future__ import annotations

from typing import List

from .models import ResearchRole, ReviewFinding, ReviewReport, Severity
from .store import ResearchStore
from .validators import validate_store


class IndependentReviewGate:
    """Deterministic Phase-1 gate; human/LLM reviewer findings can be appended later."""

    def review(self, store: ResearchStore) -> ReviewReport:
        findings: List[ReviewFinding] = []
        for index, issue in enumerate(validate_store(store), start=1):
            findings.append(
                ReviewFinding(
                    finding_id=f"RV-{index:03d}",
                    severity=issue.severity,
                    category=issue.code,
                    message=issue.message,
                )
            )
        passed = not any(f.severity in (Severity.CRITICAL, Severity.MAJOR) for f in findings)
        return ReviewReport(
            reviewer_role=ResearchRole.INDEPENDENT_REVIEWER,
            findings=findings,
            passed=passed,
        )
