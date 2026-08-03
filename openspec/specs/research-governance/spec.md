# Research Governance Specification

## Purpose

This capability defines the thesis scope, stable research questions, hypothesis
status, claim boundaries, and the rules by which evidence may strengthen or
weaken publishable conclusions.

## Requirements

### Requirement: RGV-001 Thesis scope and novelty

The project SHALL frame its primary contribution as a sparse-sensing spatial
digital twin for estimating indoor environmental fields and learning the
environmental impacts of non-networked appliances in a single room.

#### Scenario: Describing the headline contribution

- **WHEN** a thesis, IEEE manuscript, presentation, abstract, or project summary states the contribution
- **THEN** it SHALL foreground sparse IoT sensing, indoor spatial intelligence, non-networked appliance impact learning, and decision support
- **AND** it SHALL identify temperature, humidity, and illuminance as the three modeled factors
- **AND** it SHALL not present the MCP interface as the headline novelty

#### Scenario: Respecting the study boundary

- **WHEN** the scope of the implemented study is summarized
- **THEN** it SHALL be limited to a single rectangular room with reduced-order field estimation
- **AND** it SHALL not imply multi-room airflow, CFD-equivalent fidelity, automatic closed-loop control, or universal building generalization

### Requirement: RGV-002 Research-question registry

The project SHALL maintain the following stable research questions until an
approved OpenSpec change modifies them.

#### Scenario: Using the core research questions

- **WHEN** research questions are listed
- **THEN** `RQ1` SHALL ask whether eight corner sensors can support single-room temperature, humidity, and illuminance field estimation
- **AND** `RQ2` SHALL ask whether environmental observations can be used to learn spatial impacts of non-networked appliances
- **AND** `RQ3` SHALL ask whether the learned model can support explainable ranking of candidate environmental actions
- **AND** `RQ4` SHALL ask whether the model can be exposed through standardized local service tools without changing the research model

#### Scenario: Prioritizing research questions

- **WHEN** limited manuscript space requires prioritization
- **THEN** `RQ1` through `RQ3` SHALL be treated as core research questions
- **AND** `RQ4` SHALL be treated as a secondary systems-integration question

### Requirement: RGV-003 Hypothesis status

The project SHALL distinguish hypotheses supported by current evidence from
hypotheses that remain protocol-only or exploratory.

#### Scenario: Reporting currently supported hypotheses

- **WHEN** current results are interpreted
- **THEN** `H1` MAY state that the reduced-order calibrated estimator outperforms IDW on the controlled canonical-scenario field-MAE benchmark
- **AND** `H2` MAY state that sparse calibration reduces error at the unseen pillow reference point in the recorded bedroom snapshot study
- **AND** `H3` MAY state that the additive residual learner reduces residual error within the controlled scenario family under held-out and leave-one-scenario-out evaluation
- **AND** all three statements SHALL retain their evidence-class boundaries

#### Scenario: Reporting partially supported public-data positioning

- **WHEN** SML2010 and CU-BEMS results are summarized
- **THEN** `H4` MAY state that structured appliance, boundary, and response priors are most useful on aligned event or boundary-change tasks
- **AND** the summary SHALL disclose that short-horizon illuminance and high-inertia CU-BEMS tasks often favor persistence

#### Scenario: Reporting unverified recommendation efficacy

- **WHEN** actual action efficacy is discussed
- **THEN** `H5` SHALL remain not evaluated until a before/after intervention protocol produces evidence
- **AND** counterfactual ranking SHALL not be described as causal validation

### Requirement: RGV-004 Evidence support levels

Every quantitative or causal research claim SHALL be assigned an explicit
support level tied to machine-readable evidence.

#### Scenario: Classifying a claim

- **WHEN** a claim is added or updated
- **THEN** it SHALL be labeled `REPRODUCIBLE`, `DOCUMENT_ONLY`, `NEEDS_DATA`, or `NOT_EVALUATED`
- **AND** a `REPRODUCIBLE` claim SHALL identify a local evidence file and a command that can regenerate or verify it

#### Scenario: Handling missing or conflicting evidence

- **WHEN** an evidence file is absent or disagrees with a manuscript value beyond tolerance
- **THEN** the claim SHALL be reported as missing, failed, or unsupported
- **AND** the document value SHALL not override the computed result

### Requirement: RGV-005 Claim-strength discipline

Research wording SHALL be no stronger than the design and evidence that support it.

#### Scenario: Interpreting controlled simulation

- **WHEN** evidence comes from synthetic truth in canonical scenarios
- **THEN** the claim SHALL be limited to controlled simulation behavior
- **AND** it SHALL not be generalized to arbitrary real rooms or dense real-world ground truth

#### Scenario: Interpreting real-bedroom snapshots

- **WHEN** evidence comes from the seven-day bedroom snapshot dataset
- **THEN** the claim SHALL be limited to sparse calibration and an unseen point reference within those snapshots
- **AND** it SHALL not be described as full-room dense causal validation

#### Scenario: Interpreting task-aligned public datasets

- **WHEN** evidence comes from SML2010 or CU-BEMS
- **THEN** the claim SHALL be limited to shared observable forecasting or event-response tasks
- **AND** it SHALL not claim validation of the complete eight-corner 3D spatial-twin configuration

### Requirement: RGV-006 Research changes use OpenSpec

Substantive changes to the topic, method, experiments, metrics, architecture,
figures, chapter structure, or conclusions SHALL be proposed and traced through
`openspec/changes/`.

#### Scenario: Starting a substantive change

- **WHEN** a proposed edit can change a research question, method, metric, evidence level, or publishable claim
- **THEN** the change SHALL use the `research-first` schema
- **AND** it SHALL include research framing, a pre-registered protocol, delta specs, design, reproducibility, and tasks before execution

#### Scenario: Closing a research change

- **WHEN** a substantive change is ready to archive
- **THEN** it SHALL include actual evidence and claim decisions
- **AND** every applicable synchronized artifact SHALL have been rebuilt and checked for stale content

### Requirement: RGV-007 Application relevance and operating-domain discipline

The project SHALL separate numerical estimator precision from demonstrated application need and SHALL keep application claims within the current `20–30 °C` temperature domain.

#### Scenario: Discussing human comfort

- **WHEN** human comfort is used as a motivating or recommendation target
- **THEN** it SHALL be represented with explicit target bands or tolerances
- **AND** lower model MAE SHALL not be described by itself as evidence that humans require equally precise actuation

#### Scenario: Proposing a precision-critical application

- **WHEN** a closed cultivation, laboratory, or other controlled environment is proposed
- **THEN** its need for dynamic rather than merely constant environmental control SHALL be stated
- **AND** every intended temperature SHALL lie within `20–30 °C` for current-scope alignment
- **AND** missing application variables and outcome evidence SHALL be disclosed

#### Scenario: An application exceeds the current range

- **WHEN** any required operating temperature is below `20 °C` or above `30 °C`
- **THEN** the application SHALL be labeled out of current model scope
- **AND** it SHALL require new modeling, calibration, and validation before any applicability claim
