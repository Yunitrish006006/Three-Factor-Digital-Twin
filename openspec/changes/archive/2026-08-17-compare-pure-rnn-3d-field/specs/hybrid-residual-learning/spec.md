# Hybrid Residual Learning Delta Specification

## Purpose

This delta separates a standalone recurrent field baseline from the primary physics-plus-residual estimator.

## Requirements

### Requirement: HRL-011 Pure RNN spatial comparator boundary

A pure RNN 3-D field model SHALL remain an evaluation comparator unless a later research change accepts it as a production estimator component.

#### Scenario: Comparing standalone and hybrid learning

- **WHEN** pure RNN and LOO hybrid are compared
- **THEN** pure RNN SHALL predict absolute field values without physics or residual inputs
- **AND** LOO hybrid SHALL retain its additive physics-plus-residual definition
- **AND** both SHALL use the same scenario folds, deterministic training-point rule, and held-out field metric

#### Scenario: Observing a favorable or adverse RNN result

- **WHEN** pure RNN wins or loses a factor or fold
- **THEN** the observed result SHALL be retained without post-outcome architecture replacement
- **AND** production estimator behavior SHALL remain unchanged
