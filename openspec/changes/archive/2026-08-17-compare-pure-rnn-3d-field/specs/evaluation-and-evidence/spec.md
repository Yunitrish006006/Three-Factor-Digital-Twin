# Evaluation and Evidence Delta Specification

## Purpose

This delta registers a same-task pure RNN baseline for controlled full 3-D field reconstruction.

## Requirements

### Requirement: EVD-018 Same-task pure RNN 3-D field comparison

The project SHALL compare IDW, base model, pure RNN, and LOO hybrid on identical canonical controlled scenario folds, sparse observations, query grids, dense truth fields, and metric functions.

#### Scenario: Building one held-out fold

- **WHEN** one canonical scenario is held out
- **THEN** the other seven scenarios SHALL be the only source of learned RNN and hybrid parameters
- **AND** both learned models SHALL use the same deterministic 96 training points per training scenario
- **AND** the held-out sparse observation payload, query grid, and truth field SHALL be hashed before ranking methods

#### Scenario: Running the pure RNN

- **WHEN** the pure RNN predicts a held-out field point
- **THEN** it SHALL receive the canonical eight-sensor sequence and registered current query/scenario context
- **AND** it SHALL NOT receive a physics estimate, residual target, IDW prediction, target-point truth, or held-out dense truth

#### Scenario: Reporting results

- **WHEN** the eight-fold comparison completes
- **THEN** per-fold and average temperature, humidity, and illuminance full-field MAE SHALL be retained for all four methods
- **AND** training diagnostics, parity hashes, non-RNN winners, and adverse RNN folds SHALL remain visible
- **AND** the result SHALL be labeled controlled synthetic full-field evidence rather than real-room or cross-room validation
