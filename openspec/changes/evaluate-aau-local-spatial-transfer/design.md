# Design

## Data Flow

1. The E11C downloader requests only the 11 fixed gap-centered HTTP ranges and writes raw fragments under `/tmp`.
2. The manifest supplies the fixed source CSV header as schema only; the existing parser repairs nonzero fragment boundaries and aggregates only E11C observation rows to one-minute medians.
3. The local evaluator precomputes a deterministic neighbor order for every held-out sensor.
4. Every method receives identical observed temperatures and held-out targets.
5. The evaluator writes per-sensor, aggregate, bootstrap, and hypothesis-decision fields to one JSON artifact.

## Leakage Prevention

- E11B ranges are discovery evidence and are not reused for E11C metrics.
- E11C offsets and model parameters are committed before network retrieval.
- No confirmation metric selects neighborhood size, distance power, coordinate scaling, or channel exclusions.

## Failure Modes

- HTTP status other than 206, wrong byte count, or Content-Range mismatch aborts retrieval.
- Any overlap with E11B intervals aborts manifest creation.
- Missing fragments, malformed schema, insufficient minutes, or sensor-count drift remain explicit failures or `not_evaluable` outcomes.

## Artifact Synchronization

After execution, actual E11C results must propagate to canonical OpenSpec, Chinese thesis/build source, IEEE manuscript, presentation source/outlines, professor report, difficulty log, and generated DOCX/PDF/PPTX outputs.
