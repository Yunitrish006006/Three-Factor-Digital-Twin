# E15 BMC Temporal Confirmation Evidence

## ADDED Requirements

### Requirement: EVD-037 Frozen temporal confirmation protocol

The research record SHALL evaluate the exact SHA-256-pinned E14C model on the
14 preregistered, previously unused BMC files without refitting, file
substitution, or post-outcome threshold changes.

#### Scenario: Confirmation inputs remain frozen

- **WHEN** the E15 evaluator starts
- **THEN** it verifies the exact filename set, each downloaded file hash, and the frozen model hash before parsing confirmation outcomes

#### Scenario: Complete runs define uncertainty

- **WHEN** confidence intervals are computed
- **THEN** the evaluator resamples complete runs with the preregistered seed and 20,000 bootstrap replicates

### Requirement: EVD-038 Bounded confirmation interpretation

The research record SHALL preserve all E15 results and limit any supported
claim to temporal and workload transfer within the same public server dataset.

#### Scenario: A gate fails

- **WHEN** any preregistered data-quality or accuracy gate fails
- **THEN** H-ENC-08 is recorded as not supported without deleting files or changing the model

#### Scenario: Every gate passes

- **WHEN** every preregistered gate passes
- **THEN** H-ENC-08 may support a same-server temporal confirmation claim but not PC-enclosure, NTC, spatial, cross-server, or deployment claims
