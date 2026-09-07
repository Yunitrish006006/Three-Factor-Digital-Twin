# Evaluation and Evidence Delta

## ADDED Requirements

### Requirement: EVD-020 AAU Server-Room Spatial Transfer Evidence

The research repository SHALL evaluate E11B using a pre-registered deterministic sample of the AAU v4 temperature file, a traceable high-confidence 3D coordinate mapping, leave-one-sensor-out baselines, and an explicit supported/not-supported/not-evaluable decision.

#### Scenario: Deterministic external-data sampling

- **WHEN** the 706,160,545-byte AAU temperature file is sampled
- **THEN** the output records all twelve fixed byte offsets, fragment sizes, checksums, parsing exclusions, and minute aggregation counts

#### Scenario: Ambiguous coordinate mapping

- **WHEN** a channel-to-coordinate pairing cannot be independently established from official artifacts
- **THEN** the channel is excluded before metric execution and the exclusion remains visible in protocol and evidence

#### Scenario: Spatial baseline decision

- **WHEN** eligible leave-one-sensor-out metrics are available
- **THEN** the repository compares global mean, nearest neighbor, and fixed-parameter 3D IDW using macro errors and per-sensor win fraction without post-run threshold changes

#### Scenario: Adverse or insufficient result

- **WHEN** H-ENC-02 fails or eligibility is insufficient
- **THEN** the negative or not-evaluable decision is preserved and synchronized rather than replaced by an expected result
