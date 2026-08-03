# Research Artifact Synchronization Specification

## Purpose

This capability turns the repository-wide synchronization policy into
verifiable requirements for the Chinese thesis, IEEE manuscript, presentation,
figures, builders, and generated deliverables.

## Requirements

### Requirement: SYN-001 Coupled research deliverable

The Chinese thesis, English IEEE paper, presentation, and their generated
outputs SHALL remain synchronized in research scope, methods, experiments,
metrics, architecture, and conclusions.

#### Scenario: Adding a method

- **WHEN** a new research method is accepted
- **THEN** it SHALL appear in every applicable source artifact
- **AND** its role, assumptions, metrics, and limitations SHALL agree across languages and presentation formats

#### Scenario: Weakening a claim

- **WHEN** evidence requires a claim to be weakened or removed
- **THEN** the weaker wording SHALL propagate to all applicable synchronized artifacts
- **AND** no stale stronger wording SHALL remain in generated outputs

### Requirement: SYN-002 Source-of-truth discipline

Generated documents SHALL be rebuilt from their designated sources and SHALL
not be edited as substitutes for source changes.

#### Scenario: Updating the Chinese thesis

- **WHEN** Chinese thesis content changes
- **THEN** `docs/thesis/thesis_draft_zh.md` and `scripts/build_thesis_docx.py` SHALL remain logically aligned
- **AND** the thesis DOCX and PDF outputs in both designated locations SHALL be rebuilt

#### Scenario: Updating the IEEE manuscript

- **WHEN** English paper content changes
- **THEN** `docs/papers/ieee/paper.tex` SHALL remain the source of truth
- **AND** references and `docs/papers/ieee/paper.pdf` SHALL be rebuilt where applicable

#### Scenario: Updating the presentation

- **WHEN** presentation content changes
- **THEN** `scripts/build_thesis_pptx.py` SHALL remain the source of truth
- **AND** both presentation outlines and both PPTX outputs SHALL be updated where applicable

### Requirement: SYN-003 Figure synchronization

Architecture, experiment, and result figures SHALL use the same concepts,
captions, numbers, and evidence as the synchronized text artifacts.

#### Scenario: Changing a figure-relevant concept

- **WHEN** a method, architecture, dataset, result, or claim used in a figure changes
- **THEN** `docs/thesis/system_architecture_diagrams_zh.md`, applicable figure generators, `outputs/figures/architecture/`, and thesis assets SHALL be updated
- **AND** repository-structure details SHALL not replace research architecture in conceptual figures

### Requirement: SYN-004 Required rebuilds

Applicable synchronized edits SHALL execute the repository build commands and
record any unavailable tool or failed build.

#### Scenario: Rebuilding thesis and presentation outputs

- **WHEN** synchronized thesis content changes
- **THEN** the architecture, DOCX, PDF, and PPTX build scripts listed in `AGENTS.md` SHALL be run as applicable
- **AND** generated file timestamps alone SHALL not be treated as validation

#### Scenario: Rebuilding the IEEE paper

- **WHEN** IEEE source changes
- **THEN** `tectonic --keep-logs --keep-intermediates paper.tex` SHALL be run from `docs/papers/ieee`
- **AND** build errors or unavailable tooling SHALL be reported explicitly

### Requirement: SYN-005 Progress consistency

No synchronized artifact SHALL present a method, benchmark, result, or
conclusion at a later project-progress level than the others.

#### Scenario: Evidence exists in only one artifact

- **WHEN** a new metric or result appears in only one source
- **THEN** the synchronization task SHALL remain incomplete
- **AND** the research change SHALL not be archived

#### Scenario: Searching for stale content

- **WHEN** synchronized work is prepared for closure
- **THEN** old metrics, deprecated names, obsolete captions, placeholders, draft notes, and disallowed claims SHALL be searched across sources and generated text
- **AND** any unresolved occurrence SHALL be documented or removed

### Requirement: SYN-006 OpenSpec and artifact alignment

Accepted OpenSpec specs SHALL reflect the same current research behavior and
evidence level as the synchronized artifacts.

#### Scenario: Archiving a research change

- **WHEN** a change is archived
- **THEN** its accepted delta specs SHALL be synchronized into `openspec/specs/`
- **AND** research artifacts SHALL contain the same accepted scope, metrics, and claim boundaries

#### Scenario: Detecting drift

- **WHEN** OpenSpec, code, evidence, or research artifacts disagree
- **THEN** the disagreement SHALL be treated as unresolved drift
- **AND** the strongest unsupported claim SHALL be weakened until evidence and artifacts are reconciled

### Requirement: SYN-007 Research logic overview

The synchronized research artifacts SHALL provide a shared overview that links
the research gap, research questions, method components, evidence layers, and
claim boundaries without changing the accepted research content.

#### Scenario: Rendering the overview

- **WHEN** the research logic overview is generated
- **THEN** it SHALL show RQ1 through RQ3 as the core research line and RQ4 as a secondary service line
- **AND** it SHALL map the method core to controlled, real-snapshot, public-aligned, and future-intervention evidence
- **AND** it SHALL keep E8 visibly distinct as not yet causally validated

#### Scenario: Synchronizing placements

- **WHEN** the overview is used in the Chinese thesis, IEEE paper, or presentation
- **THEN** labels, arrows, evidence status, and claim boundaries SHALL agree
- **AND** the existing detailed system and execution diagrams SHALL remain available for method-level explanation

### Requirement: SYN-008 Master experiment overview synchronization

The master experiment overview SHALL agree with the current thesis sources and machine-readable evidence without introducing a separate progress level.

#### Scenario: Updating a reconciled metric

- **WHEN** reconciliation changes a metric shown in a synchronized source
- **THEN** its build source and generated outputs SHALL be rebuilt
- **AND** all applicable occurrences of the superseded value SHALL be removed or clearly labeled as legacy

#### Scenario: Reporting an unexecuted experiment

- **WHEN** E8, Kalman filtering, or another future protocol is listed
- **THEN** its status SHALL remain `NOT_EVALUATED` or protocol-only
- **AND** it SHALL not be grouped with completed empirical results
