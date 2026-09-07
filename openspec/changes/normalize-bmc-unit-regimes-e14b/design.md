# E14B Design

## Rationale

Linux hwmon documents temperature inputs in millidegree Celsius and power inputs in microwatts. OpenBMC represents temperature values with an explicit scale, including examples where `Value=34625` and `Scale=-3` means 34.625 degrees C. The CSV omits scale metadata, but its section medians form two non-overlapping regimes separated by roughly three orders for temperature and six for power.

## Leakage Control

Scale classification uses only input units and section medians, never target residuals, candidate-model performance, or accuracy gates. E14B is a retrospective data-correctness study over already opened files and cannot become confirmation evidence.

## Diagnostics

The parser SHALL retain each section's temperature scale, power scale, median indicators, concordance flag, and accepted row count. The audit SHALL compare per-file counts against the frozen E14A result.
