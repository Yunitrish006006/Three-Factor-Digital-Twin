from __future__ import annotations

import unittest

from digital_twin.research.models import (
    ClaimRecord,
    ClaimStrength,
    ComplexityInputs,
    ContradictionRecord,
    EvidenceDepth,
    EvidenceRecord,
    PaperRecord,
    ResearchRole,
    ResearchTask,
    SourceType,
)
from digital_twin.research.orchestration import AdaptiveOrchestrationPlanner, OrchestrationPolicy
from digital_twin.research.store import ResearchStore
from digital_twin.research.validators import validate_plan, validate_store


def task(task_id: str, **kwargs: int) -> ResearchTask:
    return ResearchTask(task_id=task_id, question="test question", complexity=ComplexityInputs(**kwargs))


class AdaptiveOrchestrationRegressionTests(unittest.TestCase):
    def test_single_clear_question_is_primary_only(self) -> None:
        plan = AdaptiveOrchestrationPlanner().plan(task("t1"))
        self.assertEqual(plan.assessment.mode.value, "primary-only")
        self.assertEqual([a.role for a in plan.assignments], [ResearchRole.PRIMARY])

    def test_small_lookup_is_primary_plus_scout(self) -> None:
        plan = AdaptiveOrchestrationPlanner().plan(task(
            "t2", breadth=2, expected_paper_count=5,
            recency_requirement=1, source_quality_requirement=2,
        ))
        self.assertEqual(plan.assessment.mode.value, "assisted")
        self.assertEqual(
            {a.role for a in plan.assignments},
            {ResearchRole.PRIMARY, ResearchRole.LITERATURE_SCOUT},
        )

    def test_general_review_has_scout_extractor_reviewer(self) -> None:
        plan = AdaptiveOrchestrationPlanner().plan(task(
            "t3", breadth=2, topic_count=3, expected_paper_count=20,
            methodology_diversity=2, source_quality_requirement=3,
            independent_review_need=2, uncertainty=1,
        ))
        roles = {a.role for a in plan.assignments}
        self.assertEqual(plan.assessment.mode.value, "bounded-parallel")
        self.assertTrue({
            ResearchRole.LITERATURE_SCOUT,
            ResearchRole.EVIDENCE_EXTRACTOR,
            ResearchRole.INDEPENDENT_REVIEWER,
        }.issubset(roles))

    def test_cross_discipline_conflict_is_guarded_parallel(self) -> None:
        plan = AdaptiveOrchestrationPlanner().plan(task(
            "t4", breadth=3, topic_count=6, discipline_count=4,
            expected_paper_count=40, recency_requirement=3,
            methodology_diversity=3, mixed_evidence_types=3,
            evidence_conflict=3, source_quality_requirement=3,
            statistical_comparison=3, independent_review_need=3,
            uncertainty=3,
        ))
        roles = {a.role for a in plan.assignments}
        self.assertEqual(plan.assessment.mode.value, "guarded-parallel")
        self.assertIn(ResearchRole.METHODOLOGY_ANALYST, roles)
        self.assertIn(ResearchRole.CONTRADICTION_ANALYST, roles)

    def test_agent_budget_is_never_exceeded(self) -> None:
        plan = AdaptiveOrchestrationPlanner(
            OrchestrationPolicy(max_subagents=2, max_parallelism=2)
        ).plan(task(
            "t5", breadth=3, topic_count=6, discipline_count=4,
            expected_paper_count=40, methodology_diversity=3,
            evidence_conflict=3, independent_review_need=3, uncertainty=3,
        ))
        self.assertLessEqual(plan.subagent_count, 2)
        self.assertEqual(validate_plan(plan), [])

    def test_extractor_cannot_synthesize_and_reviewer_is_independent(self) -> None:
        plan = AdaptiveOrchestrationPlanner().plan(task(
            "t6", breadth=2, expected_paper_count=20,
            methodology_diversity=2, independent_review_need=3,
            source_quality_requirement=3,
        ))
        extractor = next(a for a in plan.assignments if a.role == ResearchRole.EVIDENCE_EXTRACTOR)
        reviewer = next(a for a in plan.assignments if a.role == ResearchRole.INDEPENDENT_REVIEWER)
        self.assertFalse(extractor.participates_in_synthesis)
        self.assertFalse(reviewer.participates_in_synthesis)
        self.assertIn("t6:primary", reviewer.depends_on)


class EvidenceValidationRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = ResearchStore()
        self.store.add_paper(PaperRecord(
            paper_id="P1", title="Example", authors=["A"], year=2025,
            venue="Journal", doi="10.1/example", url=None,
            source_type=SourceType.PEER_REVIEWED_PRIMARY,
            relevance="direct", included=True,
            evidence_depth=EvidenceDepth.FULL_TEXT,
        ))
        self.store.add_evidence(EvidenceRecord(
            evidence_id="E1", paper_id="P1", research_question=None,
            hypothesis=None, study_design="controlled experiment",
            population=None, sample_size="100", dataset="benchmark",
            intervention="method A", comparison="method B", baseline="method B",
            methodology="controlled comparison", metrics=["accuracy"],
            primary_results=["A > B"], effect_size=None,
            statistical_significance=None, confidence_interval=None,
            limitations=["single benchmark"], authors_conclusion="A performs better",
            actually_supports=["A performs better on this benchmark"],
            does_not_support=["universal superiority"], locator="p. 5 results",
            evidence_depth=EvidenceDepth.FULL_TEXT,
        ))

    def test_claim_without_evidence_is_rejected(self) -> None:
        self.store.add_claim(ClaimRecord(
            "C1", "Unsupported claim", ClaimStrength.HIGH, []
        ))
        codes = {issue.code for issue in validate_store(self.store)}
        self.assertIn("claim-without-evidence", codes)

    def test_contradictory_evidence_cannot_be_silently_dropped(self) -> None:
        self.store.add_evidence(EvidenceRecord(
            evidence_id="E2", paper_id="P1", research_question=None,
            hypothesis=None, study_design="controlled experiment",
            population=None, sample_size="100", dataset="benchmark",
            intervention="method A", comparison="method B", baseline="method B",
            methodology="controlled comparison", metrics=["accuracy"],
            primary_results=["B >= A"], effect_size=None,
            statistical_significance=None, confidence_interval=None,
            limitations=[], authors_conclusion="No advantage",
            actually_supports=["no advantage"],
            does_not_support=["A is always better"], locator="appendix",
            evidence_depth=EvidenceDepth.METHODS_RESULTS,
        ))
        self.store.add_claim(ClaimRecord(
            "C2", "A performs better", ClaimStrength.MIXED, ["E1"], []
        ))
        self.store.add_contradiction(ContradictionRecord(
            "X1", "C2", ["E1"], ["E2"], "benchmark sensitivity",
            ClaimStrength.MEDIUM,
        ))
        codes = {issue.code for issue in validate_store(self.store)}
        self.assertIn("silently-dropped-contradiction", codes)


if __name__ == "__main__":
    unittest.main()
