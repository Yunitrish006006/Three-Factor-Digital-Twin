# E14C Post-run Evidence

## Run identity

- Study: E14C corrected retrospective sensitivity analysis
- Frozen model SHA-256: `609048167f2a7e261bee45e2d935c650be7a55184cdce3966b014e6cd1e5ba84`
- Result SHA-256: `90bdcbfcb483bd3abeed7900904cf45e05e48a3ecb6c931ca70f13267b57048a`
- Corrected parser/unit audit: E14B, supported
- Test status: previously opened; retrospective sensitivity only

## Observed results

The frozen inlet-plus-offset baseline obtained MAE/RMSE/P95 errors of
4.0882/5.2087/12.0000 degrees C over 3,242 rows. The frozen load-aware ridge
model obtained 1.8054/2.8001/7.1146 degrees C. It won 13 of 14 runs, and the
run-block bootstrap 95% interval for macro MAE gain was [1.4271, 2.7939]
degrees C. Its predictions remained within 37.0033 to 64.3640 degrees C.

## Decision

All retrospective accuracy, completeness, unit-concordance, and prediction
plausibility gates passed. The candidate is eligible for a new frozen
confirmation study. This does not restore an unseen-test claim for E14C and
does not establish transfer to another server, a desktop computer enclosure,
or an NTC sensor deployment.
