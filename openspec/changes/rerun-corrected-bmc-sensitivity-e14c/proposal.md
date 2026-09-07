# Change: Rerun Corrected BMC Sensitivity Analysis

## Why

E14B supports physically interpretable unit normalization, but E13 model metrics were generated from schema-contaminated inputs. A fixed retrospective rerun is needed to determine whether the unchanged candidate family is suitable for a new confirmation study.

## What Changes

- Add E14C using the exact E13 split, baselines, ridge candidates, refit rule, bootstrap, and accuracy gates.
- Require the supported E14B parser and unit-normalization result.
- Treat the original 14 test files as retrospective sensitivity data, not unseen confirmation.
- Forward a frozen candidate to a future study only if all original gates and prediction-plausibility checks pass.

## Impact

E14C may justify a new confirmation protocol. It cannot support H-ENC-06/H-ENC-07 or any physical, spatial, causal, cross-server, PC-chassis, or NTC claim.
