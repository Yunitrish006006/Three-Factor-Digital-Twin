# Research Artifact Synchronization Delta Specification

## Purpose

This delta keeps the four-method 3-D field comparison synchronized across research and professor-facing artifacts.

## Requirements

### Requirement: SYN-010 Pure RNN 3-D evidence synchronization

The pure RNN 3-D comparison SHALL use one canonical machine-readable result across the thesis, IEEE paper, presentations, field-comparison figure, professor report, and professor demo.

#### Scenario: Reporting the comparison

- **WHEN** a synchronized artifact shows the controlled full-field comparison
- **THEN** IDW, base model, pure RNN, and LOO hybrid values SHALL match the canonical evidence
- **AND** the public SML2010 temporal RNN result SHALL remain separately labeled as a different task
- **AND** the synthetic-truth and one-room boundaries SHALL remain visible
