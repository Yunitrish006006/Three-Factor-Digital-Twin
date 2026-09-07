# E14B Protocol

## Frozen Inputs and Expected Regimes

- Require the E12 manifest SHA-256 `9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74`.
- Require the E14A result SHA-256 `348d6525a7f495302a7e076f38f4705c5d3214a62d13546961cf8e1546e94833`.
- Expected raw-unit files: `202307191620.csv`, `202307201552.csv`, and `202307211550.csv`.
- Expected already-normalized files: the other 28 manifest entries.

## Section-Level Classification

- Calculate the median of raw `max(Cpu1_Temp, Cpu2_Temp)` within each accepted BMC section.
- Classify temperature as raw millidegree Celsius when the median is at least 1,000; otherwise classify it as degrees Celsius.
- Calculate the median of raw `PSU1_Total_Power + PSU2_Total_Power` in the same section.
- Classify power as raw microwatts when the median is at least 100,000; otherwise classify it as watts.
- Require the two indicators to agree on raw versus normalized regime.
- Make one classification per complete section; never switch scale row by row.

## Fixed Transformations

- Raw-unit section temperatures: multiply inlet, outlet, CPU1, and CPU2 by `0.001`.
- Raw-unit section PSU powers: multiply each PSU power by `0.000001` before summing.
- Already-normalized sections: multiply by `1.0`.
- Fan RPM remains unchanged.
- Do not clip, impute, delete, or alter timestamps.

## Gates

- Preserve exactly 4,038 accepted rows and exact per-file oracle agreement.
- Identify exactly the three preregistered raw-unit files.
- Require concordant temperature/power regimes for every section.
- Require all normalized temperatures in `[0, 150]` degrees C and summed PSU power in `[0, 5000]` W.
- Require the known raw example at `2023-07-19T07:54:52Z` to normalize to inlet 34.5, outlet 34.5, CPU1 36.5, CPU2 37.0, and summed PSU power 245 W.
- Require already-normalized fixture values to remain unchanged.
