# Change: Recover Short-Run BMC Evaluation

## Why

E12 stopped before model selection because five development files contained fewer than 30 valid BMC rows. All development files still contained at least 13 valid rows, and all 14 final-test files remained unopened. A separately preregistered recovery study can test the unchanged model question with a defensible 10-row complete-run availability gate.

## What Changes

- Add E13 using the exact E12 manifest, split, candidates, metrics, and accuracy gates.
- Change only the minimum valid rows per complete file from 30 to 10.
- Record the selected and refitted model before any final-test CSV is opened.
- Fail closed if any final-test run contains fewer than 10 valid rows.

## Impact

E13 can recover a cross-run BMC evaluation but cannot erase the E12 null result or support physical PC-chassis, NTC, spatial, causal, or cross-server claims.
