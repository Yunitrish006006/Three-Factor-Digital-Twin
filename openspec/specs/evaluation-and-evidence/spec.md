# Evaluation and Evidence Specification

## Purpose

This capability defines the experiment registry, metrics, baselines, accepted
current results, evidence classes, and automated checks that constrain all
quantitative statements in the thesis, IEEE manuscript, and presentation.

## Requirements

### Requirement: EVD-001 Evidence-class separation

Evaluation SHALL keep controlled simulation, real-room snapshots, public
task-aligned benchmarks, and intervention studies as distinct evidence classes.

#### Scenario: Combining result tables

- **WHEN** results from more than one evidence class appear together
- **THEN** each row or subsection SHALL identify its evidence class
- **AND** no aggregate conclusion SHALL erase differences in ground truth, geometry, sensing topology, or causal design

#### Scenario: Escalating a claim

- **WHEN** a claim moves from simulation to real-room or causal wording
- **THEN** a corresponding real-room or intervention evidence artifact SHALL exist
- **AND** the change SHALL be reviewed through the research-first OpenSpec workflow

### Requirement: EVD-002 Experiment registry

The project SHALL maintain experiments and validation items `E1` through `E9`
with stable meanings and explicit evidence status.

#### Scenario: Listing the current registry

- **WHEN** the experiment registry is rendered
- **THEN** `E1` SHALL mean canonical full-field reconstruction
- **AND** `E2` SHALL mean IDW baseline comparison
- **AND** `E3` SHALL mean ablation and reproducibility analysis
- **AND** `E4` SHALL mean non-networked appliance impact-learning checks
- **AND** `E5` SHALL mean the window-condition matrix and direct-input sensitivity study
- **AND** `E6` SHALL mean hybrid residual robustness
- **AND** `E7` SHALL mean real-bedroom snapshot sparse calibration
- **AND** `E8` SHALL mean real before/after action intervention validation
- **AND** `E9` SHALL mean public task-aligned benchmarking

#### Scenario: Reporting registry status

- **WHEN** current status is reported
- **THEN** `E1`, `E2`, `E3`, `E5`, `E6`, and `E7` SHALL be `REPRODUCIBLE`
- **AND** `E4` SHALL be bounded to controlled or recorded learning checks rather than real causal identification
- **AND** `E8` SHALL remain `DOCUMENT_ONLY` or `NOT_EVALUATED` until intervention evidence exists
- **AND** `E9` SHALL be `REPRODUCIBLE` only when the required public evidence JSON files exist

### Requirement: EVD-003 Metrics and comparator parity

Quantitative comparisons SHALL use declared metrics and shall evaluate competing
methods on equivalent targets, horizons, samples, and splits.

#### Scenario: Evaluating field reconstruction

- **WHEN** dense controlled fields are evaluated
- **THEN** MAE SHALL be reported separately for temperature, humidity, and illuminance
- **AND** physics, IDW, and hybrid comparisons SHALL use the same evaluation points for a given experiment

#### Scenario: Evaluating public tasks

- **WHEN** public benchmark methods are compared
- **THEN** MAE, RMSE, and Pearson correlation SHALL be available
- **AND** persistence, linear regression, and the hybrid digital-twin readout SHALL use the same task, target, horizon, and chronological split

### Requirement: EVD-004 Controlled field evidence

Current controlled-simulation evidence SHALL remain traceable to
`outputs/data/validation_summary.json` and SHALL be reproducible by
`python3 scripts/run_demo.py`.

#### Scenario: Verifying canonical scale

- **WHEN** `validation_summary.json` is verified
- **THEN** it SHALL contain eight canonical scenarios
- **AND** the window matrix evidence SHALL contain 48 cases when produced by `python3 scripts/run_window_matrix.py`

#### Scenario: Verifying average physics field MAE

- **WHEN** canonical scenario `field_mae` values are averaged
- **THEN** temperature SHALL equal `0.0474` within the registered tolerance
- **AND** humidity SHALL equal `0.1765` within the registered tolerance
- **AND** illuminance SHALL equal `2.0269` within the registered tolerance

#### Scenario: Verifying average IDW field MAE

- **WHEN** canonical scenario `idw_field_mae` values are averaged
- **THEN** temperature SHALL equal `0.1723` within the registered tolerance
- **AND** humidity SHALL equal `0.4633` within the registered tolerance
- **AND** illuminance SHALL equal `54.9052` within the registered tolerance

### Requirement: EVD-005 Hybrid robustness evidence

Hybrid residual claims SHALL use held-out and leave-one-scenario-out evidence
with sample counts and a no-Fourier comparison.

#### Scenario: Verifying the default hybrid split

- **WHEN** `outputs/data/hybrid_residual_summary.json` is verified
- **THEN** it SHALL report `576` training samples and `192` test samples
- **AND** hybrid test field MAE SHALL be `0.0020` for temperature, `0.0051` for humidity, and `0.1370` for illuminance within registered tolerances

#### Scenario: Verifying leave-one-scenario-out results

- **WHEN** `outputs/data/submission_readiness_summary.json` is verified
- **THEN** it SHALL report eight leave-one-scenario-out folds
- **AND** average hybrid field MAE SHALL be `0.0017` for temperature, `0.0059` for humidity, and `0.1407` for illuminance within registered tolerances

### Requirement: EVD-006 Real-bedroom snapshot evidence

Real-bedroom calibration claims SHALL remain traceable to the seven-day,
28-snapshot study and its unseen pillow reference point.

#### Scenario: Verifying study scale

- **WHEN** `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json` is verified
- **THEN** it SHALL report 28 snapshots collected or represented across seven days

#### Scenario: Verifying unseen-point improvement

- **WHEN** pillow-position error is compared before and after sparse calibration
- **THEN** before-calibration MAE SHALL be `0.8967 °C`, `4.1286 %`, and `309.0142 lux` within registered tolerances
- **AND** after-calibration MAE SHALL be `0.1676 °C`, `0.3939 %`, and `16.6450 lux` within registered tolerances
- **AND** the result SHALL not be described as dense full-room ground truth

### Requirement: EVD-007 Public benchmark evidence

Public benchmark conclusions SHALL preserve dataset-specific wins, losses, task
alignment, and chronological-split limitations.

#### Scenario: Interpreting SML2010

- **WHEN** the SML2010 comparison is summarized
- **THEN** it SHALL report 24 target-horizon tasks, 12 lowest-MAE outcomes, 15 wins over linear regression, and 14 wins over persistence
- **AND** it SHALL identify S3 event or boundary delta tasks as the main advantage
- **AND** it SHALL disclose short-horizon illuminance and humidity-scale limitations

#### Scenario: Interpreting CU-BEMS

- **WHEN** the CU-BEMS comparison is summarized
- **THEN** it SHALL report 12 target-horizon tasks, 9 wins over linear regression, and 0 wins over persistence
- **AND** it SHALL disclose the weakness on high-inertia zone-level and illuminance tasks

#### Scenario: Describing the mapped research method

- **WHEN** the public hybrid digital-twin result is described
- **THEN** it SHALL state that a small linear readout is fitted on the same chronological `70/30` split
- **AND** it SHALL not describe the result as a zero-shot full 3D field evaluation

### Requirement: EVD-008 Intervention evidence boundary

Action recommendation efficacy SHALL remain unverified until `E8` executes a
before/after intervention protocol with measured outcomes.

#### Scenario: No intervention evidence exists

- **WHEN** no completed `E8` evidence report and machine-readable summary exist
- **THEN** recommendation results SHALL be labeled model-based counterfactual rankings
- **AND** causal efficacy, success rate, top-1 regret, and measured benefit SHALL not be claimed

#### Scenario: Intervention evidence becomes available

- **WHEN** `E8` is completed
- **THEN** its protocol, deviations, raw observations, analysis output, uncertainty, and claim decisions SHALL be archived together
- **AND** the main spec and synchronized research artifacts SHALL be updated to the accepted bounded result

### Requirement: EVD-009 Automated result verification

The project SHALL verify manuscript numbers against machine-readable evidence
and SHALL surface missing or inconsistent results.

#### Scenario: Running the verifier

- **WHEN** `python3 scripts/verify_thesis_results.py` is executed
- **THEN** it SHALL write JSON and Markdown reports under `outputs/data/`
- **AND** each checked result SHALL receive `PASS`, `FAIL`, or `MISSING`
- **AND** each result SHALL identify its support level, source file, evidence file, tolerance, and suggested script

#### Scenario: A checked value fails

- **WHEN** computed evidence differs from a manuscript value beyond tolerance
- **THEN** verification SHALL return or record `FAIL`
- **AND** synchronized artifacts SHALL not be treated as submission-ready until the discrepancy is resolved

### Requirement: EVD-010 Cluster-aware uncertainty for repeated real-room snapshots

Real-bedroom snapshot comparisons SHALL report deterministic uncertainty that
preserves the paired structure and the repeated snapshots within each date.

#### Scenario: Computing E7 uncertainty

- **WHEN** raw and calibrated pillow errors are compared across the seven-day E7 dataset
- **THEN** bootstrap resampling SHALL use calendar date as the block
- **AND** all snapshots from a sampled date SHALL move together
- **AND** the output SHALL record seed, replicate count, confidence level, and resampling unit

#### Scenario: Reporting the uncertainty result

- **WHEN** a confidence interval for calibration improvement is reported
- **THEN** it SHALL identify the endpoint as paired mean absolute-error reduction
- **AND** it SHALL remain bounded to one room, one held-out pillow point, and the observed seven-day period
- **AND** snapshot improvement fraction SHALL NOT be labeled as an intervention success rate

#### Scenario: Detecting unstable improvement

- **WHEN** any metric's interval includes or falls below zero
- **THEN** the all-metric robustness hypothesis SHALL not be accepted
- **AND** synchronized claims SHALL report the adverse or inconclusive metric

### Requirement: EVD-011 Executable E8 analysis without evidence fabrication

The E8 analysis path SHALL expose readiness and evidence status independently
of whether real intervention trials have been collected.

#### Scenario: Running the empty repository template

- **WHEN** the E8 analyzer receives the registered template with zero completed trials
- **THEN** it SHALL emit `NOT_EVALUATED`
- **AND** all efficacy estimates SHALL be null
- **AND** it SHALL state that real intervention observations are required

#### Scenario: Running completed real trials

- **WHEN** valid completed real intervention records are supplied
- **THEN** the analyzer SHALL compute only preregistered endpoints supported by the design
- **AND** the output SHALL record trial counts, condition counts, exclusions, and unavailable metrics

#### Scenario: Running synthetic verification fixtures

- **WHEN** synthetic records are used by automated tests
- **THEN** they SHALL remain outside thesis evidence outputs
- **AND** they SHALL not change E8's evidence status or support a causal claim

### Requirement: EVD-012 Published hybrid-method transfer comparison

The project SHALL distinguish a reproducible, paper-inspired method transfer from reproduction of the cited paper's confidential data, physical model, and CNN--LSTM implementation.

#### Scenario: Running the transfer comparison

- **GIVEN** normalized SML2010 records and a compatible project model checkpoint
- **WHEN** `python3 scripts/run_oh2024_inspired_comparison.py` is executed
- **THEN** it SHALL compare persistence, direct linear regression, raw physics prior, the project mapped readout, and an Oh et al. (2024)-inspired additive residual readout
- **AND** every comparator SHALL use the same temperature targets, horizons, samples, chronological `70/30` split, and metric definitions
- **AND** the machine-readable output SHALL include `15`, `60`, and `1440` minute horizons

#### Scenario: Describing method fidelity

- **WHEN** the transfer result is presented in research artifacts
- **THEN** it SHALL state that the transferred residual learner is a fixed ridge-linear surrogate rather than the paper's CNN--LSTM
- **AND** it SHALL state that the paper's BEMS data are confidential
- **AND** it SHALL not claim reproduction of the published numerical results or direct superiority over the published model

#### Scenario: Preserving adverse results

- **WHEN** the transferred method loses to any comparator or fails the pre-registered physics-improvement threshold
- **THEN** the loss SHALL remain in the JSON evidence and synchronized narrative
- **AND** no horizon, target, feature set, or threshold SHALL be removed after observing the result without a new protocol version

### Requirement: EVD-013 Leakage-controlled next-day temperature improvement

The project SHALL evaluate next-day temperature improvements with a
chronological validation-only selection protocol and a final test partition
that is excluded from candidate and hyperparameter choice.

#### Scenario: Selecting a next-day candidate

- **GIVEN** exact SML2010 origin, lag, and target timestamps
- **WHEN** the next-day comparison is executed
- **THEN** candidate selection SHALL use only the earliest 60% training and next 10% validation rows
- **AND** the selected candidate SHALL be refitted only on the earliest 70%
- **AND** the latest 30% SHALL be used only for final metrics

#### Scenario: Auditing forecast-origin features

- **WHEN** the seasonal residual feature vector is constructed
- **THEN** it MAY use origin-time measurements, timestamp cycles, historical lags, origin-time weather forecast, and origin-derived physics
- **AND** it SHALL NOT use target-time measured indoor state, actual weather, sunlight, or device state

#### Scenario: A historical lag is unavailable

- **WHEN** an exact `t-24h` or `t-7d` lag is unavailable
- **THEN** the evaluator MAY use the nearest allowed origin/history fallback with an availability flag
- **AND** it SHALL preserve the original origin/target row and record the missing-lag count
- **AND** the fallback SHALL NOT use target-time measurements or actual target-time boundaries

#### Scenario: Reporting unsuccessful or unstable improvement

- **WHEN** either target fails to beat seasonal persistence or its daily-block bootstrap interval includes zero
- **THEN** the failure SHALL remain visible in machine-readable and synchronized research artifacts
- **AND** the project SHALL NOT claim a robust next-day advantage

#### Scenario: Running a post-primary adaptive analysis

- **WHEN** an online same-slot correction is designed after the primary test result is known
- **THEN** its candidates and validation rule SHALL be registered before its predictions are computed
- **AND** every correction at origin `t` SHALL use only daily deltas completed at or before `t`
- **AND** the result SHALL be labeled post-primary exploratory
- **AND** it SHALL NOT replace the primary hypothesis or support a confirmatory next-day claim

### Requirement: EVD-014 Leave-one-date-out sensitivity for E7

The project SHALL report a deterministic date-deletion sensitivity analysis for the seven-day E7 pillow-point comparison.

#### Scenario: Computing date-deletion folds

- **WHEN** the E7 weekly summary is produced
- **THEN** each observed date SHALL be omitted exactly once
- **AND** raw and calibrated MAE SHALL be recomputed from every remaining snapshot for temperature, humidity, and illuminance
- **AND** no date-deletion fold SHALL be removed after its result is observed

#### Scenario: Accepting the robustness hypothesis

- **WHEN** `H-E7-LODO-01` is decided
- **THEN** the minimum absolute MAE reduction across all date-deletion folds SHALL be greater than zero for all three metrics
- **AND** any zero or negative minimum SHALL be reported as not supported

#### Scenario: Reporting the bounded result

- **WHEN** the sensitivity result appears in a thesis, paper, presentation, or report
- **THEN** the number of dates, omitted-date design, and minimum reductions SHALL remain traceable to machine-readable evidence
- **AND** the result SHALL remain bounded to one room, one held-out pillow point, and the observed seven dates

### Requirement: EVD-015 Same-data vanilla RNN comparison

The project SHALL compare the professor-requested vanilla RNN with project and baseline methods using one shared public-task endpoint contract.

#### Scenario: Building the comparator dataset

- **WHEN** the RNN comparison is prepared
- **THEN** one ordered eligible-endpoint index SHALL be created before fitting any model
- **AND** every comparator SHALL use the same normalized records, four-record origin history, targets, chronological split, test endpoint IDs, and metric functions
- **AND** no comparator SHALL receive target-time measured inputs or later observations unavailable to the others

#### Scenario: Accounting for sequence warm-up

- **WHEN** four history records are required for the RNN
- **THEN** endpoints without complete history SHALL be excluded once from the shared index
- **AND** persistence, linear, physics-structured, and RNN metrics SHALL all be recomputed on the remaining identical test endpoints

#### Scenario: Reporting results

- **WHEN** `python3 scripts/run_rnn_public_comparison.py` completes
- **THEN** all target-horizon case metrics and pairwise losses SHALL remain in machine-readable evidence
- **AND** the result SHALL be descriptive without a pre-assumed RNN superiority claim
- **AND** any endpoint mismatch, non-finite training result, or missing comparator SHALL produce `NOT_EVALUATED` rather than a partial ranking

### Requirement: EVD-016 Canonical complete experiment inventory

The project SHALL maintain a consolidated E1–E9 inventory that is traceable to current machine-readable evidence and preserves adverse, missing, and out-of-domain outcomes.

#### Scenario: Rendering the inventory

- **WHEN** the complete experiment overview is generated
- **THEN** every E1–E9 item SHALL identify its evidence class, data, comparators, metrics, status, evidence path, producer command, and claim boundary
- **AND** E9 subexperiments SHALL remain distinguishable rather than being collapsed into one result

#### Scenario: Reconciling stale prose

- **WHEN** a prose number differs from the current canonical JSON
- **THEN** the prose SHALL be updated to the current value
- **AND** the mismatch SHALL not be hidden by averaging, selecting the favorable version, or leaving both versions unqualified

#### Scenario: Auditing the E5 temperature domain

- **WHEN** an E5 target-zone indoor temperature is outside `20–30 °C`
- **THEN** the row SHALL be retained as an out-of-domain stress case
- **AND** it SHALL not support current-domain applicability claims
