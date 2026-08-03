# Design

## Deliverable Structure

The master report will contain:

1. Evidence-class and status legend.
2. One-page E1–E9 experiment registry.
3. Detailed sections for each experiment.
4. E9 subexperiment table.
5. Prior-model versus improved-model comparison.
6. Supported, adverse, pending, and out-of-domain conclusions.
7. Evidence and rerun command index.

## Reconciliation Flow

`JSON evidence -> extracted current metric -> source document reconciliation -> synchronized build -> verifier -> visual QA`.

## Failure Handling

- If JSON and prose disagree, mark drift and update prose to JSON.
- If a result has no current JSON, retain `DOCUMENT_ONLY` or `NOT_EVALUATED`.
- If a generated artifact cannot be rebuilt, do not archive the change.
- If an E5 row is out of range, preserve the row but prevent it from supporting current-domain applicability.

