# Proposal: Add an Executable E8 Intervention Validation Kit

## Why

E8 currently defines a narrative before/after protocol, but it does not yet
provide a fixed machine-readable trial contract, deterministic analysis code,
or a current status artifact. This makes field execution harder and leaves room
for metric definitions to drift after data collection.

## What Changes

- Add a versioned JSON Schema and empty data-collection template for E8.
- Add a deterministic analyzer for trial validation and preregistered metrics.
- Emit an explicit `NOT_EVALUATED` summary while no completed real trials exist.
- Add tests using synthetic fixtures that are never treated as thesis evidence.
- Synchronize the executable protocol and its evidence boundary across the
  Chinese thesis, IEEE paper, and both presentation sources.

## Impact

This change improves research readiness and reproducibility. It does not provide
causal evidence and must not change E8 from `DOCUMENT_ONLY` or `NOT_EVALUATED`.

