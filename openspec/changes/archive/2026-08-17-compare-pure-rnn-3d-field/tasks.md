# Tasks

## 1. Registration

- [x] 1.1 Register `RQ-RNN3D-01`, comparator roles, eight LOO folds, model configuration, inputs, forbidden leakage paths, metrics, and failure rules before execution.
- [x] 1.2 Register pure RNN as a controlled 3-D evaluation baseline rather than a production estimator.

## 2. Implementation and Experiment

- [x] 2.1 Implement the pure spatial-sensor Elman RNN dataset and fold-local preprocessing.
- [x] 2.2 Implement same-fold IDW, base, pure RNN, and hybrid evaluation with shared hashes.
- [x] 2.3 Add unit tests for determinism, input contract, fold exclusion, no-physics inputs, and output completeness.
- [x] 2.4 Run all eight folds and write machine-readable evidence.
- [x] 2.5 Record actual metrics, adverse cases, deviations, and claim decisions in `evidence.md`.

## 3. Synchronization

- [x] 3.1 Merge accepted delta requirements into main specs.
- [x] 3.2 Update the professor report and offline demo with the four-method 3-D comparison.
- [x] 3.3 Synchronize Chinese thesis source/builder and generated DOCX/PDF outputs.
- [x] 3.4 Synchronize IEEE source/output and field-comparison figure.
- [x] 3.5 Synchronize presentation builder, both outlines, and generated decks.

## 4. Validation

- [x] 4.1 Run unit tests, OpenSpec validation, result verification, stale-text searches, and `git diff --check`.
- [x] 4.2 Visually verify rebuilt PDFs, decks, and professor demo where runtime support is available.
- [x] 4.3 Archive only after evidence decisions and every applicable synchronized artifact are complete.
