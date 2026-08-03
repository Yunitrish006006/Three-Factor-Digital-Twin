# Action Recommendation Specification

## Purpose

This capability defines explainable, model-based ranking of candidate appliance
actions against complete three-factor comfort targets and explicitly separates
counterfactual ranking from real-world causal efficacy.

## Requirements

### Requirement: ACT-001 Complete recommendation context

Action ranking SHALL require a valid scope, a current model sample or scenario,
registered candidate devices, and complete temperature, humidity, and
illuminance targets.

#### Scenario: Ranking for a point

- **WHEN** a caller supplies a valid point sample and all three target values
- **THEN** the service SHALL evaluate candidates for the registered devices
- **AND** the response SHALL identify the point, current values, targets, and ranked actions

#### Scenario: Missing a target factor

- **WHEN** any target factor is absent
- **THEN** the service SHALL reject the request
- **AND** it SHALL not generate a ranking from an implicit target

### Requirement: ACT-002 Counterfactual scoring

Candidate actions SHALL be ranked by simulated post-action comfort penalty and
predicted improvement relative to the current state.

#### Scenario: Scoring a candidate

- **WHEN** an action is evaluated
- **THEN** the model SHALL apply the candidate to a copy of the current device state
- **AND** it SHALL calculate post-action field or point values and a three-factor penalty
- **AND** it SHALL preserve the action definition and predicted improvement in the result

#### Scenario: Comparing device-specific actions

- **WHEN** compatible devices are registered
- **THEN** air-conditioner candidates MAY include mode, setpoint, airflow, angles, and swing settings
- **AND** window candidates MAY include open and close states
- **AND** light candidates MAY include on, dim, and off states

### Requirement: ACT-003 Explainable ranking output

Each ranked action SHALL expose enough information to explain why it appears in
its position.

#### Scenario: Presenting the top action

- **WHEN** ranking succeeds
- **THEN** each item SHALL include its action name, score or penalty, predicted improvement, and modeled effects
- **AND** the result SHALL distinguish the current penalty from predicted post-action penalty

#### Scenario: No useful candidate

- **WHEN** no candidate improves the modeled target penalty
- **THEN** the result SHALL preserve non-positive improvements
- **AND** it SHALL not fabricate a beneficial recommendation

### Requirement: ACT-004 Safety and scope limits

The recommendation layer SHALL remain decision support and SHALL not execute
physical appliance actions automatically.

#### Scenario: Returning a recommendation

- **WHEN** a ranking is returned through Python, Web, MCP, or an AI bridge
- **THEN** it SHALL be advisory
- **AND** it SHALL not imply remote actuation, authorization, or closed-loop control

#### Scenario: Unsafe or unsupported interpretation

- **WHEN** a requested action requires capabilities outside the registered model
- **THEN** the service SHALL reject or omit that action
- **AND** it SHALL not infer physical safety from comfort score alone

### Requirement: ACT-005 Causal validation boundary

Recommendation efficacy SHALL not be called empirically validated until a
real-room intervention study measures outcomes after executing ranked actions.

#### Scenario: Reporting current behavior

- **WHEN** only simulation ranking and bedroom calibration snapshots are available
- **THEN** the module SHALL be described as counterfactual decision support
- **AND** `H5` SHALL remain not evaluated

#### Scenario: Evaluating an intervention

- **WHEN** a before/after action trial is performed
- **THEN** the protocol SHALL compare predicted and measured comfort improvement after a fixed settling interval
- **AND** it SHOULD include no-action, human baseline, or alternative-action controls where feasible
- **AND** success rate, prediction error, direction accuracy, top-1 regret, and rank correlation SHALL be reported only when supported by the design

### Requirement: ACT-006 Preregistered intervention trial records

Real E8 action trials SHALL follow a versioned machine-readable record contract
that preserves the recommendation, executed action, target, observations,
settling interval, controls, and deviations.

#### Scenario: Recording a completed top-ranked trial

- **WHEN** a trial is labeled `COMPLETED` with condition `top_ranked`
- **THEN** the executed action SHALL equal the action with predicted rank 1
- **AND** before and after observations SHALL contain temperature, humidity, and illuminance
- **AND** the full predicted ranking and target definition SHALL be preserved

#### Scenario: Rejecting an incomplete completed trial

- **WHEN** a completed trial omits a required observation, target factor, action, or settling interval
- **THEN** the analyzer SHALL reject the record
- **AND** the record SHALL not contribute to any efficacy metric

#### Scenario: Evaluating matched action arms

- **WHEN** one environmental block contains comparable completed action arms
- **THEN** top-1 regret and rank correlation MAY be computed from the measured outcomes
- **AND** unavailable matched-arm metrics SHALL remain null rather than be inferred

### Requirement: ACT-007 Application-specific precision targets

Recommendation targets SHALL reflect application-specific tolerance bands and SHALL not infer control value from estimator precision alone.

#### Scenario: Ranking for human comfort

- **WHEN** the target application is human comfort
- **THEN** temperature, humidity, and illuminance targets SHALL include explicit tolerances or acceptable ranges
- **AND** recommendations SHALL not optimize unnecessary sub-tolerance changes as if they were demonstrated user benefits

#### Scenario: Ranking for a precision-critical process

- **WHEN** a cultivation or laboratory process is proposed
- **THEN** its dynamic setpoint schedule, tolerance, temperature-domain fit, missing variables, and process endpoint SHALL be defined before action efficacy is evaluated
- **AND** the current comfort penalty SHALL not be relabeled as a biological or laboratory quality metric
