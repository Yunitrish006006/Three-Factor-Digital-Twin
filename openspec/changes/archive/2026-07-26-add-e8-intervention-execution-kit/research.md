# Research Registration

## Research Question

`RQ-E8-PREP-01`: Can a preregistered intervention-record contract and
deterministic analyzer make E8 directly executable while preventing incomplete
or synthetic records from being interpreted as causal evidence?

## Hypothesis

`H-E8-PREP-01`: The analyzer will reject incomplete completed trials, reproduce
known metric values for synthetic test fixtures, and emit `NOT_EVALUATED` with
null efficacy metrics for the zero-trial repository template.

## Claim Registry

| Claim ID | Claim | Evidence class | Boundary |
| --- | --- | --- | --- |
| `CLM-E8-PREP-01` | The repository contains an executable, preregistered E8 data and analysis path. | method readiness | No recommendation efficacy result; no real trial has been completed. |

## Decision Rule

Accept `H-E8-PREP-01` only if all E8 analyzer tests pass, the empty template
produces `NOT_EVALUATED`, and the summary contains no numeric efficacy claims.

