# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-026 E11F shall confirm only the frozen E11H commissioning map

The confirmation workflow SHALL apply the exact hash-frozen E11H models to all eligible E11F observations without refitting or record exclusion.

#### Scenario: E11F includes calendar dates seen during development

- **WHEN** E11F dates overlap E11E or E11H dates
- **THEN** the overlap is reported and the claim remains bounded to unseen bytes within one campaign

#### Scenario: Every H-ENC-05 gate passes

- **WHEN** aggregate, tail, coverage, bootstrap, and absolute-error gates all pass
- **THEN** H-ENC-05 is supported only as calibration-assisted within-campaign predictive confirmation

#### Scenario: Any H-ENC-05 gate fails

- **WHEN** one or more frozen confirmation gates fail
- **THEN** H-ENC-05 is not supported and no E11F-driven model revision is permitted

