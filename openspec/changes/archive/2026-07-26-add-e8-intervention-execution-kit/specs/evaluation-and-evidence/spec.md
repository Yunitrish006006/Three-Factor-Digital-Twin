# Evaluation and Evidence Delta Specification

## ADDED Requirements

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

