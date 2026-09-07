# Design

## Data Flow

1. The downloader validates all fixed ranges against E11B and E11C exclusions.
2. It retrieves the schema header and eleven independent observation fragments with HTTP `206` checks, byte counts, and SHA-256 hashes.
3. The evaluator verifies the frozen E11C metadata hash and resolves exactly 42 sensor-role assignments.
4. Complete one-minute snapshots feed paired leave-one-sensor-out predictions.
5. The evaluator writes metrics, bootstrap uncertainty, condition booleans, and the hypothesis decision to one JSON artifact.

## Failure Policy

Schema mismatch, an incomplete role map, overlap, non-`206` responses, incorrect byte counts, or insufficient same-role peers stops the run before a scientific decision is emitted.

