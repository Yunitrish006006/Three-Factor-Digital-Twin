# Design

## Package Placement

Add `digital_twin/research/` as research-process infrastructure separate from estimator, Web, and MCP layers.

## Modules
- `models.py`: tasks, assignments, sources, evidence, claims, graph, review, replay events.
- `orchestration.py`: weights, normalization, thresholds, budgets, assignment waves.
- `store.py`: shared paper/evidence registry, deduplication, graph data, replay log.
- `validators.py`: deterministic plan and evidence invariants.
- `review.py`: independent deterministic review gate.
- `scripts/research_orchestration.py`: minimal CLI.

## Data Flow
```text
Task JSON -> ResearchTask -> ComplexityAssessment -> OrchestrationPlan
          -> bounded assignment waves -> ResearchStore
          -> Primary ClaimRecord -> validators
          -> IndependentReviewGate -> replay log
```

## Compatibility
- Python 3.9+.
- Standard library only in Phase 1.
- No estimator API changes.
- Runtime-specific subagent spawning remains outside the core planner.

## Failure Modes
- out-of-range ordinal factors are clamped to 0-3;
- count dimensions are normalized through fixed thresholds;
- agent budget truncates optional roles;
- dangling evidence/graph IDs fail validation;
- contradiction records omitted from claims fail validation;
- replay events are never inferred retroactively.
