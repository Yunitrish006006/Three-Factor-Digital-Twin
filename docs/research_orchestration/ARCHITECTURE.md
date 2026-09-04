# Research Adaptive Orchestration Architecture

## Purpose

This subsystem makes literature research, evidence extraction, contradiction handling, review, and replay explicit project behavior rather than prompt-only convention.

```text
ResearchTask
 -> ComplexityAssessment
 -> OrchestrationPlan
 -> bounded Assignments
 -> shared Paper/Evidence Store
 -> Evidence Graph
 -> Primary synthesis
 -> Independent Review Gate
 -> append-only Research Activity
 -> Replay
```

Agent prose is never evidence truth. A publishable claim is valid only when its `ClaimRecord` points to actual `EvidenceRecord` objects, which point to registered papers and source locators.

## Layering

```text
Research Profiles
  literature-review / systematic-review / technical-research
  scientific-evidence-review / product-market / policy / data-analysis
        |
        v
Adaptive Orchestration Core
  complexity scoring -> mode -> agent budget -> assignment waves
        |
        v
Research Roles
  Primary / Scout / Extractor / Methodology / Contradiction / Reviewer
        |
        v
Evidence Core
  PaperRegistry / Evidence / Claim / Contradiction / EvidenceGraph
        |
        v
Quality Gates
  plan validator / evidence validator / independent review
        |
        v
Activity + Replay
```

Common orchestration/evidence semantics remain profile-neutral. Future profiles supply domain-specific source types, quality rules, methodology checks, evidence fields, and citation style.

## Deterministic complexity scoring

Phase 1 uses explicit structured factors rather than hidden LLM-only routing. Every factor is normalized to 0-3, multiplied by committed weights, and included in the plan explanation.

| Score | Mode | Default behavior |
| ---: | --- | --- |
| 0-6 | `primary-only` | Primary only |
| 7-15 | `assisted` | Scout + Primary |
| 16-38 | `bounded-parallel` | Scout + Extractor + Primary + Reviewer |
| 39+ | `guarded-parallel` | Scout + Extractor + Methodology + Contradiction + Primary + Reviewer |

Changing weights or thresholds is a policy/code change and must update regressions.

## Assignment waves

```text
Wave 1: Literature Scout
Wave 2: Evidence Extractor / Methodology Analyst / Contradiction Analyst
Wave 3: Primary synthesis
Wave 4: Independent Reviewer
```

All assignments carry dependencies, evidence requirements, forbidden assumptions, output contracts, and `can_spawn_subagents=False` in Phase 1. If a runtime cannot spawn agents, Primary executes these same waves sequentially.

## Role boundaries

- **Primary:** scope, synthesis, conflict resolution, claim strength, final conclusion.
- **Literature Scout:** discovery, deduplication, primary/secondary classification, contrary evidence.
- **Evidence Extractor:** bounded paper IDs only; structured evidence; no synthesis.
- **Methodology Analyst:** design validity, leakage, confounding, comparability, statistics, external validity, reproducibility.
- **Contradiction Analyst:** explicit support/contradiction matrix.
- **Independent Reviewer:** post-synthesis only; no participation in original synthesis.

## Evidence truth

Phase 1 source-of-truth objects:
- `PaperRecord`: identity, source type, inclusion/exclusion rationale, evidence depth.
- `EvidenceRecord`: study design, sample/dataset, method, metrics, results, statistics, limitations, author conclusion, actual support boundary, locator.
- `ClaimRecord`: claim language plus supporting and contradicting evidence IDs.
- `ContradictionRecord`: explicit conflicting evidence and explanation.
- `GraphNode` / `GraphEdge`: typed Evidence Graph primitives.

Graph relations include `studies`, `supports`, `contradicts`, `qualifies`, `uses-method`, `uses-dataset`, `evaluates`, `compares-with`, `measures`, `reports`, `cites`, `replicates`, `fails-to-replicate`, `limited-by`, and `derived-from`.

## Shared registry

`ResearchStore` is the shared registry and reuse boundary. Papers deduplicate by normalized DOI first, then normalized title/year. Multiple roles should reuse existing paper/evidence records instead of rereading the same paper without purpose.

Phase 1 uses in-memory records plus JSON export so contracts can stabilize before adding SQLite or external search connectors.

## Review gate

The deterministic gate currently catches:
- claim without evidence;
- missing/orphan evidence;
- contradictory evidence registered but omitted from the claim;
- high-strength claim based only on abstract/secondary evidence depth;
- causal wording backed only by explicitly observational evidence;
- dangling/invalid graph edges;
- agent-budget violations;
- extractor synthesis violations;
- reviewer independence/order violations.

A later LLM/human reviewer may add findings but cannot bypass deterministic failures.

## Research activity and replay

`ResearchEvent` is append-only and sequence ordered. Events represent actual completed research actions such as `paper_discovered`, `evidence_extracted`, `claim_revised`, and `reviewer_finding`.

Replay is not a fabricated agent lifecycle. The system never invents events for work that did not occur.

## Source-of-truth boundaries

```text
Orchestration policy truth -> code + regression tests
Bibliographic truth         -> PaperRecord
Empirical evidence truth    -> EvidenceRecord + source locator
Claim truth                 -> ClaimRecord + Evidence relations
Conflict truth              -> ContradictionRecord
Review truth                -> ReviewReport
Process history truth       -> ResearchEvent log
Natural-language summaries  -> derived views only
```

This subsystem is research-process infrastructure. It does not change the digital-twin estimator or current thesis evidence claims by itself.
