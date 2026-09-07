# E13 Research Questions and Hypotheses

## Research Question

After replacing E12's unsupported 30-row availability threshold with a preregistered 10-row threshold derived only from development files, does the unchanged sparse BMC virtual sensor pass the original cross-run accuracy gates on unopened final-test files?

## Hypothesis H-ENC-07

The frozen ridge model will improve pooled MAE, RMSE, and P95 absolute error by at least 0.20 degrees C, improve macro run MAE by at least 0.20 degrees C, have a 10,000-sample run-bootstrap 95% confidence-interval lower bound above zero, and win on at least 9 of 14 test runs.

## Null and Adverse Outcomes

- Any test run below 10 valid rows causes a data-availability failure.
- Any failed accuracy gate results in `h_enc_07_not_supported`.
- E12 remains `h_enc_06_not_supported`; E13 is a distinct recovery experiment, not a replacement result.
