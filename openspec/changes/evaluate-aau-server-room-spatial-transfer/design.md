# Design

## Data Flow

1. A range downloader retrieves deterministic fragments and records request offsets and source metadata.
2. A parser repairs fragment boundaries, validates the expected header, and performs minute aggregation.
3. A room manifest provides normalized meter coordinates and source labels for 42 channels.
4. A leave-one-sensor-out evaluator computes three fixed baselines without fitted parameters.
5. A JSON result stores provenance, data-quality counts, per-sensor metrics, aggregate metrics, and the hypothesis decision.

## Separation of Concerns

- Downloaded AAU data is external evidence and is not committed.
- Coordinate mapping is committed because it is a derived, reviewable research artifact.
- Evaluation code does not infer or repair unknown channel coordinates.
- Research conclusions consume only the generated JSON, not console summaries.

## Failure Handling

- Header mismatch, ignored Range requests, malformed records, or insufficient eligible data produce an explicit failed/not-evaluable output.
- The evaluator does not silently drop individual sensors from an otherwise eligible snapshot.
- Ambiguous cooling channels remain excluded until a separate mapping audit resolves them.
