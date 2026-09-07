# E12 Design

## Estimator

The virtual sensor uses measurements normally exposed by a server BMC. `thermal_pair` uses inlet and outlet temperature. `load_aware` adds mean chassis-fan speed and summed PSU power. `load_aware_interactions` additionally uses outlet-minus-inlet temperature and PSU-power per mean fan krpm. Training means and standard deviations are frozen with the ridge coefficients.

## Leakage Control

All transformations, offsets, coefficient fits, and candidate decisions use only the permitted split. Rows from one source file never appear in more than one split. The final-test files are loaded only after the selected configuration is frozen and recorded.

## Interpretation

The target is a component temperature, not a room coordinate. This experiment tests load-aware sparse virtual sensing under cross-run shift; it is supporting evidence for IoT intelligence, not direct evidence for the thesis spatial-field model.
