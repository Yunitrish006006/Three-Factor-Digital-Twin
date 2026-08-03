# Reproducibility and Data Governance Specification

## Purpose

This capability defines executable research pipelines, input provenance,
determinism, evidence persistence, missing-data behavior, and repository data
boundaries.

## Requirements

### Requirement: RPD-001 Reproducible experiment entrypoint

The project SHALL provide a documented root-level command that orchestrates the
thesis experiment pipeline and preserves failures.

#### Scenario: Running the full pipeline

- **WHEN** `python3 scripts/run_all_thesis_experiments.py` is executed
- **THEN** it SHALL prepare data, run controlled scenarios, run the window matrix, run hybrid residual experiments, run robustness and bedroom studies unless skipped, run available public benchmarks, build public figures when possible, and verify thesis results
- **AND** failed subprocesses SHALL be listed before the command exits unsuccessfully

#### Scenario: Public data is unavailable

- **WHEN** required normalized public inputs do not exist
- **THEN** the pipeline SHALL skip public benchmark execution with a visible message
- **AND** verification SHALL mark dependent evidence as missing or needing data rather than inventing results

### Requirement: RPD-002 Public-data provenance and licensing

Public data SHALL retain dataset identity, source, license, raw-to-normalized
mapping, and task-alignment limitations.

#### Scenario: Using SML2010

- **WHEN** SML2010 is prepared
- **THEN** its source DOI and CC BY 4.0 license SHALL be documented
- **AND** normalized files SHALL preserve the fields needed for the S1, S2, and S3 task families

#### Scenario: Using CU-BEMS

- **WHEN** CU-BEMS is prepared
- **THEN** its source publication or repository version and CC BY 4.0 license SHALL be documented
- **AND** normalized files SHALL preserve the fields needed for the C1, C2, and C3 task families

#### Scenario: Version-controlling large data

- **WHEN** raw or normalized public datasets are generated or downloaded
- **THEN** repository ignore rules SHALL keep designated large data outside normal source commits
- **AND** committed summaries SHALL retain enough provenance to reacquire and normalize the data

### Requirement: RPD-003 Deterministic model experiments

Randomized experiments SHALL expose and record seeds, splits, and sample counts.

#### Scenario: Running hybrid residual training

- **WHEN** no seed override is supplied
- **THEN** seed `42` SHALL be used
- **AND** the output summary SHALL record the seed and scenario split

#### Scenario: Running public benchmarks

- **WHEN** time-series public tasks are split
- **THEN** the split SHALL be chronological `70/30`
- **AND** future observations SHALL not be used to train predictions for earlier test observations

### Requirement: RPD-004 Machine-readable evidence

Every quantitative result used in synchronized research artifacts SHALL be
derivable from a named machine-readable output.

#### Scenario: Publishing a metric

- **WHEN** a metric enters the thesis, IEEE paper, presentation, or figure
- **THEN** its evidence path, producer script, aggregation, and tolerance SHALL be known
- **AND** a verifier or documented calculation SHALL reproduce it

#### Scenario: Updating an output format

- **WHEN** an evidence JSON schema or key changes
- **THEN** result verification, document builders, figures, and OpenSpec evidence contracts SHALL be updated together

### Requirement: RPD-005 Failure and missing-evidence visibility

Reproduction workflows SHALL not convert missing inputs, failed commands, or
conflicting results into successful evidence.

#### Scenario: Evidence file missing

- **WHEN** a required output does not exist
- **THEN** the result SHALL be `MISSING` or `NEEDS_DATA`
- **AND** the suggested producer command SHALL be identified where known

#### Scenario: Result mismatch

- **WHEN** a computed value differs from a synchronized artifact beyond tolerance
- **THEN** the verification status SHALL be `FAIL`
- **AND** the discrepancy SHALL block an unqualified submission-ready claim

### Requirement: RPD-006 Verification suite

Research changes SHALL run checks proportional to the affected behavior and
shall include the repository test suite when code or services change.

#### Scenario: Changing code or service behavior

- **WHEN** core, physics, neural, MCP, Web, scripts, or data-processing behavior changes
- **THEN** `python3 -m unittest discover -s tests` SHALL pass
- **AND** relevant experiment and result-verification commands SHALL run

#### Scenario: Changing only OpenSpec structure

- **WHEN** OpenSpec configuration, schemas, templates, specs, or changes are edited
- **THEN** `python3 scripts/validate_research_openspec.py` SHALL pass
- **AND** the OpenSpec CLI validator SHOULD also pass when the CLI is available

### Requirement: RPD-007 Comparator data-parity audit

Model rankings SHALL be reproducible from a shared endpoint index and SHALL disclose any non-data structural prior.

#### Scenario: Comparing RNN and project methods

- **WHEN** a public-task model comparison is produced
- **THEN** endpoint IDs or a deterministic endpoint hash, train/test counts, timestamp ranges, history length, feature availability, and exclusions SHALL be recorded
- **AND** every ranked comparator SHALL use the same test endpoint IDs

#### Scenario: A method has extra learned data

- **WHEN** a comparator uses pretrained weights learned from another dataset
- **THEN** that additional data source SHALL be disclosed
- **AND** the method SHALL be excluded from the primary same-data ranking unless every compared data-driven method receives an equivalent training-data contract
