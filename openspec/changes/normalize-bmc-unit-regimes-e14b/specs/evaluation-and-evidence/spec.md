# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-033 E14B shall normalize BMC units at section level

The research parser SHALL infer one concordant temperature/power unit regime per BMC section and apply only the preregistered powers-of-ten scales.

#### Scenario: A raw hwmon/OpenBMC section is found

- **WHEN** median CPU temperature is at least 1,000 and median summed PSU power is at least 100,000
- **THEN** temperatures SHALL be multiplied by `10^-3` and PSU powers by `10^-6`

#### Scenario: An already-normalized section is found

- **WHEN** both median indicators are below their thresholds
- **THEN** temperature and power values SHALL remain unchanged

#### Scenario: Unit indicators disagree

- **WHEN** only one median indicator crosses its threshold
- **THEN** H-DATA-02 SHALL be unsupported and the section SHALL be reported without silent regime substitution

### Requirement: EVD-034 E14B shall preserve unit-normalization evidence boundaries

The research artifacts SHALL treat E14B as retrospective data-correctness evidence and SHALL not describe normalized E13 metrics as unseen confirmation.

#### Scenario: All E14B gates pass

- **WHEN** exactly three files use raw scales, 4,038 rows are preserved, and all ranges and examples pass
- **THEN** H-DATA-02 may support physically interpretable BMC unit normalization only

#### Scenario: Model confirmation is requested

- **WHEN** normalized data are later used for virtual sensing
- **THEN** final confirmation SHALL use separately preregistered complete files not opened by E13 or E14 analyses
