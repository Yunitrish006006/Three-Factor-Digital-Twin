# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-029 E13 shall preserve E12 while recovering short complete runs

The research workflow SHALL retain E12 as a data-quality null result and SHALL treat E13 as a separately preregistered experiment whose only protocol change is a 10-row complete-file availability threshold.

#### Scenario: E13 development begins

- **WHEN** the E13 runner loads development files
- **THEN** it SHALL verify the exact E12 manifest hash
- **AND** it SHALL retain the E12 split, model candidates, accuracy gates, and bootstrap settings

#### Scenario: A short final-test file is found

- **WHEN** any final-test file has fewer than 10 valid rows
- **THEN** H-ENC-07 SHALL be unsupported with a structured data-availability result

### Requirement: EVD-030 E13 shall freeze before opening final-test files

The E13 runner SHALL persist and hash the selected and refitted model before opening any final-test CSV.

#### Scenario: Development succeeds

- **WHEN** all training and selection files pass the 10-row gate
- **THEN** the selected baseline, ridge features, lambda, scaling, and coefficients SHALL be written before final-test parsing

#### Scenario: Final metrics are available

- **WHEN** all final-test files are evaluable
- **THEN** H-ENC-07 SHALL be supported only if every unchanged E12 accuracy gate passes
- **AND** the claim SHALL remain limited to within-server cross-run BMC virtual sensing
