# Proposal: Add Research Adaptive Orchestration

## Why

The repository already has evidence/OpenSpec governance for the thesis, but literature research itself is still largely prompt-time behavior. This change adds an executable research-process kernel so orchestration, evidence boundaries, contradiction handling, review, and replay become project behavior rather than agent memory.

## Changes

### Change RAO-C1: Adaptive planning
- **From:** no project-level deterministic planner selects research depth and role count.
- **To:** add a scored `ResearchTask -> ComplexityAssessment -> OrchestrationPlan` pipeline with `primary-only`, `assisted`, `bounded-parallel`, and `guarded-parallel`.
- **Reason:** avoid both under-research and agent explosion.
- **Impact:** research infrastructure only; no digital-twin estimator or thesis result changes.

### Change RAO-C2: Structured evidence truth
- **From:** literature notes may exist primarily as prose.
- **To:** add paper, evidence, claim, contradiction, graph, review, and activity records with deterministic validation.
- **Reason:** claims must trace to actual paper evidence and preserve adverse findings.
- **Impact:** claim-neutral tooling change.

### Change RAO-C3: Independent review gate
- **From:** review discipline is not represented as an executable literature-synthesis gate.
- **To:** add a post-synthesis independent reviewer role and deterministic review validation.
- **Reason:** reduce citation laundering, unsupported claims, confirmation bias, and overclaiming.
- **Impact:** research workflow only.

## Synchronized artifacts

This Phase-1 infrastructure change does not alter thesis method, experiment results, metrics, figures, or conclusions. Chinese thesis, IEEE manuscript, and presentation outputs therefore do not require content synchronization.

## Completion Criteria
- [x] Architecture and source-of-truth boundaries documented.
- [x] First-version data models and deterministic planner implemented in isolated skeleton.
- [x] Regression tests cover required orchestration/evidence invariants in isolated skeleton.
- [x] Code integrated on a feature branch.
- [ ] Run repository OpenSpec validation and targeted/full test suites on the integrated branch.
- [ ] Create `evidence.md` from actual integrated runs.
