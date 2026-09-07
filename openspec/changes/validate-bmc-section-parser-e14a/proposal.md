# Change: Validate the BMC Section-Aware Parser

## Why

E13's extreme errors were traced to a parser that reused the first BMC header across later InfluxDB sections and mapped host counters into thermal fields. Model robustness cannot be studied until source semantics are parsed correctly.

## What Changes

- Add E14A as a parser-correctness study with no model refit or accuracy claim.
- Reset schema state at every `#group` and accept only complete BMC sections.
- Compare production parser counts against an independently implemented raw-line oracle on all 31 frozen files.
- Preserve E12 and E13 outcomes while marking E13 numerical metrics as parser-invalidated.

## Impact

This change affects data provenance and evidence validity. It does not establish virtual-sensor performance, PC-chassis transfer, NTC accuracy, or spatial estimation accuracy.
