from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .models import (
    ClaimStrength,
    EvidenceDepth,
    GraphNodeType,
    OrchestrationPlan,
    RelationType,
    ResearchRole,
    Severity,
)
from .store import ResearchStore


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    code: str
    message: str


CAUSAL_TERMS = re.compile(r"\b(causes?|caused|leads to|results in|improves?|reduces?)\b", re.IGNORECASE)
OBSERVATIONAL_TERMS = re.compile(r"observational|cross-sectional|retrospective|correlational", re.IGNORECASE)


def validate_plan(plan: OrchestrationPlan) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if plan.subagent_count > plan.max_subagents:
        issues.append(ValidationIssue(Severity.CRITICAL, "agent-budget", "subagent count exceeds configured budget"))
    if plan.max_parallelism < 1:
        issues.append(ValidationIssue(Severity.CRITICAL, "parallelism", "max_parallelism must be >= 1"))

    reviewer = [a for a in plan.assignments if a.role == ResearchRole.INDEPENDENT_REVIEWER]
    if reviewer:
        r = reviewer[0]
        if r.participates_in_synthesis:
            issues.append(ValidationIssue(Severity.CRITICAL, "reviewer-independence", "reviewer must not participate in original synthesis"))
        if f"{plan.task_id}:primary" not in r.depends_on:
            issues.append(ValidationIssue(Severity.CRITICAL, "reviewer-order", "reviewer must run after primary synthesis"))

    for assignment in plan.assignments:
        if assignment.can_spawn_subagents:
            issues.append(ValidationIssue(Severity.MAJOR, "nested-spawn", f"{assignment.assignment_id} may not spawn subagents in Phase 1"))
        if assignment.role == ResearchRole.EVIDENCE_EXTRACTOR and assignment.participates_in_synthesis:
            issues.append(ValidationIssue(Severity.CRITICAL, "extractor-synthesis", "Evidence Extractor must not perform final synthesis"))
    return issues


def validate_store(store: ResearchStore) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for evidence in store.evidence.values():
        if evidence.paper_id not in store.papers:
            issues.append(ValidationIssue(Severity.CRITICAL, "orphan-evidence", f"{evidence.evidence_id} references missing paper {evidence.paper_id}"))

    for claim in store.claims.values():
        if not claim.supporting_evidence_ids:
            issues.append(ValidationIssue(Severity.CRITICAL, "claim-without-evidence", f"{claim.claim_id} has no supporting evidence"))
        missing = [eid for eid in claim.supporting_evidence_ids + claim.contradicting_evidence_ids if eid not in store.evidence]
        if missing:
            issues.append(ValidationIssue(Severity.CRITICAL, "missing-evidence", f"{claim.claim_id} references missing evidence: {missing}"))

        if claim.strength == ClaimStrength.HIGH:
            depths = [store.evidence[eid].evidence_depth for eid in claim.supporting_evidence_ids if eid in store.evidence]
            if depths and all(depth in (EvidenceDepth.ABSTRACT_ONLY, EvidenceDepth.SECONDARY_ONLY) for depth in depths):
                issues.append(ValidationIssue(Severity.MAJOR, "weak-depth-high-claim", f"{claim.claim_id} is high-strength but only shallow evidence was reviewed"))

        if CAUSAL_TERMS.search(claim.text):
            designs = [store.evidence[eid].study_design or "" for eid in claim.supporting_evidence_ids if eid in store.evidence]
            if designs and all(OBSERVATIONAL_TERMS.search(d) for d in designs):
                issues.append(ValidationIssue(Severity.MAJOR, "correlation-causation", f"{claim.claim_id} uses causal language with observational evidence"))

    for contradiction in store.contradictions.values():
        claim = store.claims.get(contradiction.claim_id)
        if claim is None:
            issues.append(ValidationIssue(Severity.CRITICAL, "orphan-contradiction", f"{contradiction.contradiction_id} references missing claim"))
            continue
        omitted = [eid for eid in contradiction.contradicting_evidence_ids if eid not in claim.contradicting_evidence_ids]
        if omitted:
            issues.append(ValidationIssue(Severity.CRITICAL, "silently-dropped-contradiction", f"{claim.claim_id} omits contradictory evidence: {omitted}"))

    for edge in store.graph_edges:
        if edge.source_id not in store.graph_nodes or edge.target_id not in store.graph_nodes:
            issues.append(ValidationIssue(Severity.CRITICAL, "dangling-graph-edge", f"graph edge {edge.source_id} -> {edge.target_id} is dangling"))
            continue
        src = store.graph_nodes[edge.source_id].node_type
        dst = store.graph_nodes[edge.target_id].node_type
        if edge.relation == RelationType.SUPPORTS and not ({src, dst} == {GraphNodeType.CLAIM, GraphNodeType.EVIDENCE}):
            issues.append(ValidationIssue(Severity.MAJOR, "invalid-support-edge", "supports relation must connect Claim and Evidence nodes"))
    return issues


def has_blocking_issues(issues: List[ValidationIssue]) -> bool:
    return any(issue.severity in (Severity.CRITICAL, Severity.MAJOR) for issue in issues)
