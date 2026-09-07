# Proposal: Evaluate AAU Server-Room Spatial Transfer

## Motivation

E11A showed that BMC time-series telemetry was too sparse for the proposed equipment-enclosure thermal baseline. The AAU server-room dataset adds 3D geometry, 48 PT100 temperature channels, 16 air-speed channels, and rack power. E11B will test the narrower claim that sparse same-time temperature observations can reconstruct held-out locations in a real server-room geometry.

## Scope

- Build a traceable channel-to-coordinate manifest from the official CAD log and annotated measurement figures.
- Evaluate deterministic leave-one-sensor-out temperature reconstruction on 42 high-confidence locations.
- Compare global mean, nearest-neighbor, and 3D inverse-distance weighting baselines.
- Preserve adverse, null, excluded, and missing results.

## Non-goals

- No CFD simulation or CFD accuracy claim.
- No causal cooling-control or energy-saving claim.
- No use of the six cooling-unit channels whose left/right coordinate mapping remains ambiguous.
- No redistribution of the original AAU files while the record lacks an explicit machine-readable license.

## Completion Criteria

- [x] The sampling protocol and coordinate exclusions are fixed before metric execution.
- [x] A machine-readable 42-point room design passes room-design validation.
- [x] Baseline output records provenance, exclusions, per-sensor metrics, and aggregate metrics.
- [x] Evidence and synchronized thesis, IEEE, and presentation artifacts report the actual result.
