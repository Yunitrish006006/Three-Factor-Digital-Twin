from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import (
    Assignment,
    ComplexityAssessment,
    ComplexityInputs,
    OrchestrationMode,
    OrchestrationPlan,
    ResearchRole,
    ResearchTask,
)


@dataclass(frozen=True)
class OrchestrationPolicy:
    max_subagents: int = 5
    max_parallelism: int = 3


WEIGHTS: Dict[str, int] = {
    "breadth": 2,
    "topic_count": 1,
    "discipline_count": 2,
    "expected_paper_count": 1,
    "recency_requirement": 1,
    "methodology_diversity": 2,
    "mixed_evidence_types": 1,
    "evidence_conflict": 2,
    "source_quality_requirement": 1,
    "statistical_comparison": 2,
    "independent_review_need": 2,
    "uncertainty": 2,
}


def _bounded_level(value: int) -> int:
    return max(0, min(3, int(value)))


def _count_level(value: int, thresholds: tuple[int, int, int]) -> int:
    if value <= thresholds[0]:
        return 0
    if value <= thresholds[1]:
        return 1
    if value <= thresholds[2]:
        return 2
    return 3


def normalize_components(inputs: ComplexityInputs) -> Dict[str, int]:
    return {
        "breadth": _bounded_level(inputs.breadth),
        "topic_count": _count_level(inputs.topic_count, (1, 2, 4)),
        "discipline_count": _count_level(inputs.discipline_count, (1, 2, 3)),
        "expected_paper_count": _count_level(inputs.expected_paper_count, (3, 10, 30)),
        "recency_requirement": _bounded_level(inputs.recency_requirement),
        "methodology_diversity": _bounded_level(inputs.methodology_diversity),
        "mixed_evidence_types": _bounded_level(inputs.mixed_evidence_types),
        "evidence_conflict": _bounded_level(inputs.evidence_conflict),
        "source_quality_requirement": _bounded_level(inputs.source_quality_requirement),
        "statistical_comparison": _bounded_level(inputs.statistical_comparison),
        "independent_review_need": _bounded_level(inputs.independent_review_need),
        "uncertainty": _bounded_level(inputs.uncertainty),
    }


def assess_complexity(task: ResearchTask) -> ComplexityAssessment:
    components = normalize_components(task.complexity)
    weighted = {name: level * WEIGHTS[name] for name, level in components.items()}
    score = sum(weighted.values())
    max_score = sum(3 * weight for weight in WEIGHTS.values())

    if score <= 6:
        mode = OrchestrationMode.PRIMARY_ONLY
    elif score <= 15:
        mode = OrchestrationMode.ASSISTED
    elif score <= 38:
        mode = OrchestrationMode.BOUNDED_PARALLEL
    else:
        mode = OrchestrationMode.GUARDED_PARALLEL

    explanation = [
        f"{name}={components[name]} x {WEIGHTS[name]} => {weighted[name]}"
        for name in WEIGHTS
        if components[name] > 0
    ]
    explanation.append(f"total={score}/{max_score} -> {mode.value}")
    return ComplexityAssessment(score, max_score, mode, components, explanation)


class AdaptiveOrchestrationPlanner:
    def __init__(self, policy: Optional[OrchestrationPolicy] = None) -> None:
        self.policy = policy or OrchestrationPolicy()

    def plan(self, task: ResearchTask) -> OrchestrationPlan:
        assessment = assess_complexity(task)
        assignments = self._assignments_for(task, assessment.mode)
        return OrchestrationPlan(
            task_id=task.task_id,
            assessment=assessment,
            assignments=assignments,
            max_subagents=self.policy.max_subagents,
            max_parallelism=self.policy.max_parallelism,
        )

    def _assignments_for(self, task: ResearchTask, mode: OrchestrationMode) -> List[Assignment]:
        roles: List[ResearchRole]
        if mode == OrchestrationMode.PRIMARY_ONLY:
            roles = [ResearchRole.PRIMARY]
        elif mode == OrchestrationMode.ASSISTED:
            roles = [ResearchRole.LITERATURE_SCOUT, ResearchRole.PRIMARY]
        elif mode == OrchestrationMode.BOUNDED_PARALLEL:
            roles = [
                ResearchRole.LITERATURE_SCOUT,
                ResearchRole.EVIDENCE_EXTRACTOR,
                ResearchRole.PRIMARY,
                ResearchRole.INDEPENDENT_REVIEWER,
            ]
        else:
            roles = [
                ResearchRole.LITERATURE_SCOUT,
                ResearchRole.EVIDENCE_EXTRACTOR,
                ResearchRole.METHODOLOGY_ANALYST,
                ResearchRole.CONTRADICTION_ANALYST,
                ResearchRole.PRIMARY,
                ResearchRole.INDEPENDENT_REVIEWER,
            ]

        subagents = [r for r in roles if r != ResearchRole.PRIMARY]
        subagents = subagents[: self.policy.max_subagents]
        if ResearchRole.INDEPENDENT_REVIEWER in roles and ResearchRole.INDEPENDENT_REVIEWER not in subagents:
            if self.policy.max_subagents > 0:
                subagents[-1:] = [ResearchRole.INDEPENDENT_REVIEWER]
        roles = [r for r in roles if r == ResearchRole.PRIMARY or r in subagents]

        assignments: List[Assignment] = []
        for index, role in enumerate(roles):
            assignments.append(self._make_assignment(task, role, index, roles))
        return assignments

    def _make_assignment(self, task: ResearchTask, role: ResearchRole, index: int, roles: List[ResearchRole]) -> Assignment:
        output_by_role = {
            ResearchRole.PRIMARY: ["bounded synthesis", "claim table", "open questions"],
            ResearchRole.LITERATURE_SCOUT: ["paper registry candidates", "inclusion/exclusion reasons"],
            ResearchRole.EVIDENCE_EXTRACTOR: ["structured evidence records"],
            ResearchRole.METHODOLOGY_ANALYST: ["methodology validity findings", "comparability notes"],
            ResearchRole.CONTRADICTION_ANALYST: ["claim-evidence contradiction matrix"],
            ResearchRole.INDEPENDENT_REVIEWER: ["severity-based review findings", "gate decision"],
        }
        wave_by_role = {
            ResearchRole.LITERATURE_SCOUT: 1,
            ResearchRole.EVIDENCE_EXTRACTOR: 2,
            ResearchRole.METHODOLOGY_ANALYST: 2,
            ResearchRole.CONTRADICTION_ANALYST: 2,
            ResearchRole.PRIMARY: 3,
            ResearchRole.INDEPENDENT_REVIEWER: 4,
        }
        forbidden = [
            "fabricate papers, DOI values, authors, results, or evidence locators",
            "treat agent prose as evidence truth",
            "silently drop contradictory or adverse evidence",
        ]
        if role != ResearchRole.PRIMARY:
            forbidden.append("perform final synthesis")
        if role == ResearchRole.EVIDENCE_EXTRACTOR:
            forbidden.append("expand beyond the bounded assigned paper scope")
        if role == ResearchRole.INDEPENDENT_REVIEWER:
            forbidden.append("participate in original synthesis")

        deps: List[str] = []
        if role == ResearchRole.EVIDENCE_EXTRACTOR and ResearchRole.LITERATURE_SCOUT in roles:
            deps = [f"{task.task_id}:literature-scout"]
        elif role in (ResearchRole.METHODOLOGY_ANALYST, ResearchRole.CONTRADICTION_ANALYST):
            deps = [f"{task.task_id}:evidence-extractor"] if ResearchRole.EVIDENCE_EXTRACTOR in roles else []
        elif role == ResearchRole.PRIMARY:
            deps = [f"{task.task_id}:{r.value}" for r in roles if r not in (ResearchRole.PRIMARY, ResearchRole.INDEPENDENT_REVIEWER)]
        elif role == ResearchRole.INDEPENDENT_REVIEWER:
            deps = [f"{task.task_id}:primary"]

        return Assignment(
            assignment_id=f"{task.task_id}:{role.value}",
            role=role,
            research_scope=task.question,
            paper_scope="bounded to papers admitted by the shared paper registry; extractor assignments must enumerate paper IDs",
            date_scope=task.date_range,
            inclusion_criteria=list(task.inclusion_criteria),
            exclusion_criteria=list(task.exclusion_criteria),
            output_schema=output_by_role[role],
            evidence_requirements=[
                "record source type and evidence depth",
                "record exact paper/evidence identifiers for factual claims",
                "prefer original studies when available",
            ],
            forbidden_assumptions=forbidden,
            expected_deliverable="; ".join(output_by_role[role]),
            wave=wave_by_role[role],
            depends_on=deps,
            can_spawn_subagents=False,
            participates_in_synthesis=(role == ResearchRole.PRIMARY),
        )
