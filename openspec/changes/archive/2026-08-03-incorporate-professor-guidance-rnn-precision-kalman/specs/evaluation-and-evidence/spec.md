# Evaluation and Evidence Delta

## ADDED Requirements

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

## MODIFIED Requirements

## REMOVED Requirements
