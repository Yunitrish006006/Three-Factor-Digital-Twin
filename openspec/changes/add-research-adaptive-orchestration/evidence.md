# Evidence: Research Adaptive Orchestration Phase 1

## Run metadata

- Branch: `feature/research-adaptive-orchestration-phase1`
- Integrated head evaluated: `d9bc599af0d8137b761c2816589527bc1ca17dc1`
- CI environment: GitHub Actions, Ubuntu, Python 3.12.14
- Python tests workflow run: `33921402030`
- Python test matrix workflow run: `33921402072`
- Evidence date (UTC): 2026-09-04
- No threshold, fixture, or expected-route changes were made after observing these integrated results.

## Actual integrated results

### OpenSpec validation

Command:

```bash
python scripts/validate_research_openspec.py
```

Observed result:

```text
Research OpenSpec validation passed: 14 spec files, 108 requirements, 206 scenarios, 2 active changes.
```

Decision: PASS.

### Targeted Research Adaptive Orchestration regressions

Command:

```bash
python -m unittest -v tests/test_research_orchestration.py
```

Observed result:

```text
Ran 8 tests in 0.001s
OK
```

The matrix job for `tests/test_research_orchestration.py` also completed successfully.

Decision: PASS.

### Full repository unittest suite

Command:

```bash
python -m unittest discover -s tests
```

Observed result:

```text
Ran 169 tests in 66.915s
OK
```

Decision: PASS. No unrelated or pre-existing failures were observed in this run.

### Existing CI matrix

All ten configured matrix modules completed successfully, including:

- sensor roles;
- digital twin core;
- architecture diagrams;
- hybrid residual;
- Gemma bridge;
- Web demo;
- MCP server;
- public dataset benchmark;
- public dataset model comparison;
- Research Adaptive Orchestration.

Decision: PASS.

## Hypothesis decisions

### H-RAO-01

**Hypothesis:** fixed task fixtures produce stable orchestration modes and remain within configured subagent budgets.

**Evidence:** routing regressions cover `primary-only`, `assisted`, `bounded-parallel`, and `guarded-parallel`; the explicit budget regression passed in both targeted and matrix CI.

**Decision:** SUPPORTED for the registered deterministic software fixtures.

### H-RAO-02

**Hypothesis:** a claim with zero supporting evidence fails validation.

**Evidence:** `test_claim_without_evidence_is_rejected` passed.

**Decision:** SUPPORTED as a software invariant.

### H-RAO-03

**Hypothesis:** contradictory evidence registered for a claim cannot be omitted silently.

**Evidence:** `test_contradictory_evidence_cannot_be_silently_dropped` passed and requires the `silently-dropped-contradiction` validator finding.

**Decision:** SUPPORTED as a software invariant.

### H-RAO-04

**Hypothesis:** Evidence Extractor cannot perform final synthesis and Independent Reviewer cannot participate in original synthesis.

**Evidence:** role-boundary regression passed; reviewer ordering requires dependency on Primary synthesis.

**Decision:** SUPPORTED as a software invariant.

## Deviations and adverse results

- No registered Phase-1 routing or evidence-integrity regression failed.
- No full-suite regression failure was observed.
- This evidence does **not** establish that multi-agent execution improves scientific accuracy, literature recall, or research efficiency. It establishes only that the registered orchestration and evidence-governance invariants are executable and enforced by tests.
- Live scholarly search adapters, full-text acquisition, persistent database storage, runtime-specific subagent spawning, semantic citation verification, and meta-analysis remain outside Phase 1.

## Claim decision

Phase 1 supports the bounded claim that the project now contains an executable deterministic Research Adaptive Orchestration skeleton with enforceable agent budgets, role boundaries, claim-to-evidence requirements, contradiction retention, independent review ordering, and replay data structures.

It does not support a claim that the orchestration policy is scientifically optimal or that any particular agent topology outperforms another in research quality.
