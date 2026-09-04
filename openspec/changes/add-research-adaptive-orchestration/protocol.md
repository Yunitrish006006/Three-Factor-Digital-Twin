# Protocol

## Units of Analysis
- one `ResearchTask` fixture for routing;
- one `OrchestrationPlan` for budget/role-boundary checks;
- one `ResearchStore` state for evidence-validation checks.

## Deterministic Fixtures
1. Single clear question -> `primary-only`.
2. Small literature lookup -> `assisted`.
3. General literature review -> `bounded-parallel`.
4. Cross-disciplinary high-conflict research -> `guarded-parallel`.

## Decision Criteria
- exact mode equality for all routing fixtures;
- `subagent_count <= max_subagents`;
- zero plan-validation issues for valid plans;
- expected validator code for invalid evidence states.

## Leakage / Post-hoc Controls

Fixtures and expected route classes are registered before integrated repository execution. Threshold changes after observing integrated failures require a protocol revision.

## Commands
```bash
python3 -m unittest tests/test_research_orchestration.py -v
python3 scripts/validate_research_openspec.py
python3 -m unittest discover -s tests
```

## Evidence

Actual outputs, commit IDs, Python version, deviations, and hypothesis decisions belong in `evidence.md` only after execution.
