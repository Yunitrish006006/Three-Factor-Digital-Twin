# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-035 E14C shall rerun the unchanged model pipeline retrospectively

The research workflow SHALL apply the unchanged E13 candidate family and gates to E14B-normalized data without introducing post hoc model candidates.

#### Scenario: Corrected development data are available

- **WHEN** the exact E14B result hash is verified
- **THEN** baseline and ridge selection SHALL use only the original training and selection files
- **AND** the corrected frozen model SHALL be persisted before retrospective-test loading

#### Scenario: Corrected retrospective metrics are available

- **WHEN** all 14 original test files have been reevaluated
- **THEN** eligibility SHALL require every original accuracy gate and the `[-50, 200]` prediction-plausibility gate

### Requirement: EVD-036 E14C shall not convert retrospective sensitivity into confirmation

The research artifacts SHALL describe E14C only as candidate-eligibility evidence because its test files were opened during E13 and E14 diagnostics.

#### Scenario: All E14C gates pass

- **WHEN** the candidate is marked eligible
- **THEN** a new confirmation SHALL use separately preregistered unused complete files

#### Scenario: Any E14C gate fails

- **WHEN** the candidate is marked ineligible
- **THEN** the failed gate SHALL be retained and no confirmation shall be claimed
