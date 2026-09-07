# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-027 E12 shall evaluate cross-run sparse BMC virtual sensing

The research system SHALL evaluate a frozen sparse BMC virtual sensor on complete date-disjoint source files that were unavailable during model and candidate selection.

#### Scenario: Final-test isolation

- **WHEN** E12 model selection is completed
- **THEN** the selected feature set and ridge penalty SHALL be recorded before final-test rows are evaluated
- **AND** no final-test file SHALL contribute to offsets, scaling, coefficients, or candidate selection

#### Scenario: Multi-gate decision

- **WHEN** E12 final-test metrics are available
- **THEN** H-ENC-06 SHALL be supported only if pooled MAE, RMSE, and P95 gains are each at least 0.20 degrees C
- **AND** macro run MAE gain is at least 0.20 degrees C
- **AND** the run-bootstrap 95% confidence-interval lower bound is above zero
- **AND** the model wins on at least 9 of 14 test runs

### Requirement: EVD-028 E12 shall preserve BMC provenance and claim boundaries

The research artifacts SHALL distinguish within-server cross-run evidence from PC-chassis, NTC-hardware, spatial, cross-server, and causal evidence.

#### Scenario: Positive result

- **WHEN** all H-ENC-06 gates pass
- **THEN** the claim SHALL remain limited to the frozen public BMC dataset and server platform

#### Scenario: Null or adverse result

- **WHEN** any H-ENC-06 gate fails or required data are unavailable
- **THEN** the failure SHALL be retained in evidence and synchronized artifacts without post hoc threshold changes

#### Scenario: Mutable upstream source

- **WHEN** an upstream branch file is downloaded
- **THEN** its source URL, split, byte count, and SHA-256 SHALL be frozen
- **AND** any later byte mismatch SHALL stop evaluation rather than silently update evidence

#### Scenario: Split overlap

- **WHEN** the E12 manifest is finalized
- **THEN** training, selection, and final-test filenames SHALL be mutually disjoint
