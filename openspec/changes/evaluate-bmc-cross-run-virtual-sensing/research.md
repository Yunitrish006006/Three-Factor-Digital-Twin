# E12 Research Questions and Hypotheses

## Research Question

Can a sparse, load-aware virtual sensor estimate the maximum CPU temperature more accurately than a strong single-temperature offset baseline on complete BMC runs collected on later dates and under unseen workloads or fan policies?

## Hypothesis H-ENC-06

A frozen ridge model selected without access to final-test files will improve pooled MAE, RMSE, and P95 absolute error by at least 0.20 degrees C, improve macro run MAE by at least 0.20 degrees C, have a run-bootstrap 95% confidence-interval lower bound above zero, and win on at least 9 of 14 test runs.

## Null and Adverse Outcomes

- If any gate fails, H-ENC-06 is not supported.
- Missing required columns, insufficient valid rows, unstable coefficients, or workload-dependent reversals remain reportable outcomes.
- A positive result supports only within-server cross-run virtual sensing. It does not prove spatial reconstruction, causal appliance effects, transfer to a PC chassis, or NTC hardware accuracy.
