# Proposal: Develop AAU Hierarchical Role-Local Reconstruction

## Motivation

E11D confirmed that fixed sensor roles improve over a global mean, but its MAE is 1.6517 C and P95 is 5.4886 C. Per-role MAE is highest at rack backs (2.0372 C). E11C separately showed aggregate value from local geometry. E11E therefore studies whether role semantics and local geometry can be combined without reusing E11C or E11D observations.

## Proposed Change

Use a new development split to compare preregistered role-local IDW and hierarchical role-mean/local-IDW blends against the frozen E11C local-IDW and E11D role-mean baselines. E11E selects at most one candidate; it does not confirm H-ENC-05. A further untouched E11F split is reserved for confirmation.

## Boundaries

- E11B, E11C, and E11D observations are not used for candidate scoring.
- E11D may motivate the research question but may not tune E11E candidates.
- E11E is model development, not new evidence of generalization.
- Failure to pass the forwarding gate is retained as a valid result.

