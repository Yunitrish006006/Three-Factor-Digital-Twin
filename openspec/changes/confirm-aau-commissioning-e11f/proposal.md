# Proposal: Confirm AAU Commissioning Calibration on E11F

## Why

E11H passed every development gate after two-day commissioning calibration. The reserved E11F byte ranges now provide a one-time, untouched confirmation opportunity for the exact frozen sensor map.

## What Changes

- Download only the eleven preregistered E11F byte ranges.
- Verify raw-fragment and frozen E11H result hashes.
- Apply E11H models without fitting, selection, or threshold changes.
- Test H-ENC-05 as bounded within-campaign predictive confirmation.

## Scope

E11F is unseen-byte confirmation within the AAU campaign. It is not a new physical enclosure, calendar-day-independent by assumption, an NTC hardware test, or evidence of airflow causality.

