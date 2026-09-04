# Phase 1 implementation plan

## Goal

Deliver a small executable research-governance kernel before adding live scholarly search connectors or a full multi-agent runtime.

## Deliverables

| Item | Phase 1 |
| --- | --- |
| Research task schema | `ResearchTask`, `ComplexityInputs` |
| Adaptive planner | deterministic score, four modes, explicit budget |
| Research roles | enums + assignment constraints |
| Assignment schema | scope, criteria, output schema, evidence rules, forbidden assumptions, waves |
| Paper registry | DOI/title-year dedup |
| Evidence schema | structured extraction + evidence depth |
| Claim ↔ Evidence | claim records + typed graph |
| Contradictions | explicit records + silent-drop validator |
| Independent review | post-synthesis deterministic gate |
| Activity/replay | append-only event sequence |
| CLI | `scripts/research_orchestration.py` |
| Tests | routing + evidence-governance regressions |

## Required regressions

- single clear question -> Primary only;
- small literature lookup -> Primary + Scout;
- general literature review -> Scout + Extractor + Reviewer around Primary;
- cross-disciplinary high-conflict task -> guarded parallel;
- no agent-budget overflow;
- Evidence Extractor cannot synthesize;
- Reviewer remains independent;
- claim without evidence fails;
- contradictory evidence cannot be silently dropped.

## Deferred

- Crossref/OpenAlex/Semantic Scholar/PubMed adapters;
- PDF acquisition and bounded full-text scheduling;
- SQLite/content-addressed persistence;
- runtime-specific subagent spawning;
- domain methodology plug-ins;
- PRISMA/systematic-review exports;
- meta-analysis computation;
- citation formatter integration;
- LLM-assisted reviewer findings beyond deterministic gates.

These are deferred until core contracts and validators are stable.
