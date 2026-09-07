# Proposal: Evaluate AAU Role-Conditioned Transfer

## Motivation

E11B showed that global geometry-only IDW did not beat nearest-neighbor interpolation. E11C then showed an aggregate gain for local IDW, but only 21 of 42 sensors improved. Data-center literature distinguishes rack-front/cold-aisle and rack-back/hot-aisle measurements, so categorical thermal role is a plausible missing variable.

## Proposed Change

Run a new, disjoint AAU v4 confirmation experiment. Compare a role-conditioned leave-one-sensor-out mean against a role-agnostic global mean using a role map frozen before retrieval of E11D observations.

## Boundaries

- Do not tune role definitions, model parameters, or thresholds on E11D.
- Do not reuse E11B or E11C observation byte ranges.
- Treat this as secondary enclosure-transfer evidence, not the IoTaIS headline contribution.
- Preserve adverse, null, failed, and missing outcomes.

