# Research Artifact Synchronization Delta Specification

## Purpose

This delta makes the professor-facing evidence demo a synchronized artifact without elevating interface behavior into research evidence.

## Requirements

### Requirement: SYN-009 Professor evidence demo synchronization

The professor-facing offline demo and live demo guide SHALL remain synchronized with canonical machine-readable evidence and method-status boundaries.

#### Scenario: Building the offline demo

- **WHEN** the professor evidence page is generated
- **THEN** displayed metrics SHALL come from current committed JSON evidence
- **AND** RNN and Kalman evidence classes, negative results, 20–30 °C limits, and E8 status SHALL remain visible

#### Scenario: Demonstrating live behavior

- **WHEN** the live Web demo is shown
- **THEN** room estimation, device interaction, point query, and action ranking MAY be demonstrated
- **AND** UI behavior SHALL not be counted as a quantitative experiment or causal validation
