# Proposal: E15 Frozen BMC Temporal Confirmation

## Motivation

E14C showed a strong result only in a retrospective sensitivity analysis
because its test bytes had already been opened during parser repair. A new,
untouched file set is required before making a confirmation claim.

## Proposed change

Evaluate the exact E14C frozen inlet baseline and load-aware ridge model on 14
complete BMC exports dated from 2023-08-02 through 2024-05-24. Do not refit,
select features, tune thresholds, or replace files after loading outcomes.

## Scope boundary

The study tests temporal and workload transfer within one Phytium S2500
server dataset. It excludes physical NTC experiments, desktop PC enclosures,
cross-server transfer, spatial fields, and closed-loop control.
