from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class OrchestrationMode(str, Enum):
    PRIMARY_ONLY = "primary-only"
    ASSISTED = "assisted"
    BOUNDED_PARALLEL = "bounded-parallel"
    GUARDED_PARALLEL = "guarded-parallel"


class ResearchRole(str, Enum):
    PRIMARY = "primary"
    LITERATURE_SCOUT = "literature-scout"
    EVIDENCE_EXTRACTOR = "evidence-extractor"
    METHODOLOGY_ANALYST = "methodology-analyst"
    CONTRADICTION_ANALYST = "contradiction-analyst"
    INDEPENDENT_REVIEWER = "independent-reviewer"


class SourceType(str, Enum):
    PEER_REVIEWED_PRIMARY = "peer-reviewed-primary-research"
    SYSTEMATIC_REVIEW = "systematic-review"
    META_ANALYSIS = "meta-analysis"
    CONFERENCE_PAPER = "conference-paper"
    JOURNAL_ARTICLE = "journal-article"
    PREPRINT = "preprint"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical-report"
    BENCHMARK_PAPER = "benchmark-paper"
    DATASET_PAPER = "dataset-paper"
    COMMENTARY = "commentary-opinion"
    SECONDARY_REPORTING = "secondary-reporting"
    DISCOVERY_ONLY = "discovery-only"


class EvidenceDepth(str, Enum):
    FULL_TEXT = "full-text-reviewed"
    METHODS_RESULTS = "methods-results-reviewed"
    ABSTRACT_ONLY = "abstract-only"
    SECONDARY_ONLY = "secondary-citation-only"


class ClaimStrength(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MIXED = "mixed"
    INSUFFICIENT = "insufficient"


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ActivityType(str, Enum):
    RESEARCH_STARTED = "research_started"
    ORCHESTRATION_PLANNED = "orchestration_planned"
    SEARCH_STARTED = "search_started"
    PAPER_DISCOVERED = "paper_discovered"
    PAPER_INCLUDED = "paper_included"
    PAPER_EXCLUDED = "paper_excluded"
    EVIDENCE_EXTRACTED = "evidence_extracted"
    METHODOLOGY_REVIEWED = "methodology_reviewed"
    CONTRADICTION_FOUND = "contradiction_found"
    CLAIM_CREATED = "claim_created"
    CLAIM_REVISED = "claim_revised"
    REVIEWER_FINDING = "reviewer_finding"
    SYNTHESIS_UPDATED = "synthesis_updated"
    RESEARCH_COMPLETED = "research_completed"


class GraphNodeType(str, Enum):
    RESEARCH_QUESTION = "research-question"
    HYPOTHESIS = "hypothesis"
    PAPER = "paper"
    STUDY = "study"
    DATASET = "dataset"
    METHOD = "method"
    POPULATION = "population"
    METRIC = "metric"
    RESULT = "result"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    LIMITATION = "limitation"
    CONTRADICTION = "contradiction"
    CITATION = "citation"


class RelationType(str, Enum):
    STUDIES = "studies"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    QUALIFIES = "qualifies"
    USES_METHOD = "uses-method"
    USES_DATASET = "uses-dataset"
    EVALUATES = "evaluates"
    COMPARES_WITH = "compares-with"
    MEASURES = "measures"
    REPORTS = "reports"
    CITES = "cites"
    REPLICATES = "replicates"
    FAILS_TO_REPLICATE = "fails-to-replicate"
    LIMITED_BY = "limited-by"
    DERIVED_FROM = "derived-from"


@dataclass(frozen=True)
class ComplexityInputs:
    breadth: int = 0
    topic_count: int = 1
    discipline_count: int = 1
    expected_paper_count: int = 1
    recency_requirement: int = 0
    methodology_diversity: int = 0
    mixed_evidence_types: int = 0
    evidence_conflict: int = 0
    source_quality_requirement: int = 1
    statistical_comparison: int = 0
    independent_review_need: int = 0
    uncertainty: int = 0


@dataclass(frozen=True)
class ResearchTask:
    task_id: str
    question: str
    profile: str = "literature-review"
    date_range: Optional[str] = None
    languages: List[str] = field(default_factory=lambda: ["en"])
    paper_type_constraints: List[str] = field(default_factory=list)
    inclusion_criteria: List[str] = field(default_factory=list)
    exclusion_criteria: List[str] = field(default_factory=list)
    complexity: ComplexityInputs = field(default_factory=ComplexityInputs)


@dataclass(frozen=True)
class ComplexityAssessment:
    score: int
    max_score: int
    mode: OrchestrationMode
    component_scores: Dict[str, int]
    explanation: List[str]


@dataclass(frozen=True)
class Assignment:
    assignment_id: str
    role: ResearchRole
    research_scope: str
    paper_scope: str
    date_scope: Optional[str]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    output_schema: List[str]
    evidence_requirements: List[str]
    forbidden_assumptions: List[str]
    expected_deliverable: str
    wave: int
    depends_on: List[str] = field(default_factory=list)
    can_spawn_subagents: bool = False
    participates_in_synthesis: bool = False


@dataclass(frozen=True)
class OrchestrationPlan:
    task_id: str
    assessment: ComplexityAssessment
    assignments: List[Assignment]
    max_subagents: int
    max_parallelism: int

    @property
    def subagent_count(self) -> int:
        return sum(1 for a in self.assignments if a.role != ResearchRole.PRIMARY)


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    source_type: SourceType
    relevance: str
    inclusion_reason: Optional[str] = None
    exclusion_reason: Optional[str] = None
    evidence_depth: EvidenceDepth = EvidenceDepth.ABSTRACT_ONLY
    included: bool = False


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    paper_id: str
    research_question: Optional[str]
    hypothesis: Optional[str]
    study_design: Optional[str]
    population: Optional[str]
    sample_size: Optional[str]
    dataset: Optional[str]
    intervention: Optional[str]
    comparison: Optional[str]
    baseline: Optional[str]
    methodology: Optional[str]
    metrics: List[str]
    primary_results: List[str]
    effect_size: Optional[str]
    statistical_significance: Optional[str]
    confidence_interval: Optional[str]
    limitations: List[str]
    authors_conclusion: Optional[str]
    actually_supports: List[str]
    does_not_support: List[str]
    locator: str
    evidence_depth: EvidenceDepth


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    text: str
    strength: ClaimStrength
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContradictionRecord:
    contradiction_id: str
    claim_id: str
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str]
    possible_explanation: str
    confidence: ClaimStrength


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: GraphNodeType
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    relation: RelationType
    target_id: str
    evidence_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str
    severity: Severity
    category: str
    message: str
    claim_id: Optional[str] = None
    evidence_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReviewReport:
    reviewer_role: ResearchRole
    findings: List[ReviewFinding]
    passed: bool


@dataclass(frozen=True)
class ResearchEvent:
    sequence: int
    event_type: ActivityType
    timestamp: str
    actor: str
    payload: Dict[str, Any]

    @staticmethod
    def create(sequence: int, event_type: ActivityType, actor: str, payload: Dict[str, Any]) -> "ResearchEvent":
        return ResearchEvent(
            sequence=sequence,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            payload=dict(payload),
        )


def to_dict(value: Any) -> Dict[str, Any]:
    return asdict(value)
