# E14B Research Questions and Hypotheses

## Research Question

Can section-level scale inference, grounded in official hwmon/OpenBMC unit conventions, normalize the two observed BMC unit regimes without deleting rows or changing already normalized sections?

## Hypothesis H-DATA-02

Exactly three preregistered files will be classified as raw-unit sections by concordant temperature and power indicators; applying fixed temperature `10^-3` and power `10^-6` scales will retain all 4,038 rows, place all inlet/outlet/CPU temperatures in `[0, 150]` degrees C and summed PSU power in `[0, 5000]` W, and leave the other 28 files numerically unchanged.

## Null and Adverse Outcomes

- A temperature/power regime disagreement leaves H-DATA-02 unsupported.
- Any additional raw-unit file, row-count change, or post-normalization range failure leaves H-DATA-02 unsupported.
- E14B does not choose scales from model residuals or test accuracy.
