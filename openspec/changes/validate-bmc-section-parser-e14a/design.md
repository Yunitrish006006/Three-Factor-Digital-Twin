# E14A Design

## Separation of Responsibilities

The production parser returns normalized BMC rows and section diagnostics. The oracle returns only lexical counts and section metadata. Exact count agreement is necessary but not sufficient, so explicit measurement/device checks and a known-host-row exclusion are additional gates.

## Invalidated Evidence Handling

E13 remains an executed study, but its numerical accuracy metrics cannot support a model claim because inputs were semantically misparsed. E14A may invalidate those metrics; it may not overwrite the original JSON or present corrected E13 metrics as confirmation.

## No Modeling

No baseline, ridge, Huber, clipping, scaling, bootstrap, or prediction interval is run in E14A. Robust modeling is deferred until parser correctness is supported.
