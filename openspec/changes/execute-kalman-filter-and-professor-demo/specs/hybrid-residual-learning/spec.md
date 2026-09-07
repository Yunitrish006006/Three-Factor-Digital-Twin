# Hybrid Residual Learning Delta Specification

## Purpose

This delta constrains the role of an executed Kalman comparator relative to the primary spatial estimator and residual learner.

## Requirements

### Requirement: HRL-010 Kalman comparator placement

An executed Kalman filtering baseline SHALL remain a temporal state-estimation comparator unless a separate research change integrates it with the primary spatial estimator.

#### Scenario: Completing a controlled filtering benchmark

- **WHEN** the registered injected-noise benchmark completes
- **THEN** its status MAY change from `NOT_EVALUATED` to `COMPLETE` for that benchmark only
- **AND** the result SHALL not silently replace reduced-order physics, sparse calibration, or hybrid residual correction

#### Scenario: Proposing real deployment

- **WHEN** Kalman filtering is proposed for a physical sensing node or online model update
- **THEN** real sensor noise, missingness, covariance drift, state definition, and independent reference measurements SHALL be registered separately
- **AND** the controlled injected-noise result SHALL not be reused as deployment validation
