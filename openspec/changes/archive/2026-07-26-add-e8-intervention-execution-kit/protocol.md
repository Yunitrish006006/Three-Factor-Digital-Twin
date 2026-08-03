# Protocol

## Design

Each real intervention record represents one action arm within a matched
environmental block. A record contains:

- study, room, block, trial, time, and target-scope identifiers;
- complete temperature, humidity, and illuminance target/tolerance/weight values;
- complete before and after target observations;
- the system's full predicted action ranking;
- the action actually executed, condition label, and settling interval;
- before/after external boundary observations and protocol deviations.

## Preregistered Endpoints

- `actual_improvement = penalty_before - penalty_after`
- absolute prediction error
- top-ranked success rate where `actual_improvement > 0`
- per-factor direction agreement
- top-1 regret only for matched blocks with the required action arms
- Spearman rank correlation only for matched blocks with comparable action arms

The analyzer computes penalty from recorded observations and target parameters;
it does not trust manually entered penalty totals.

## Readiness Execution

Run:

```bash
python3 scripts/analyze_e8_intervention_trials.py
```

The default repository template contains no trials and must produce
`outputs/data/e8_intervention_summary.json` with:

- `evidence_status: NOT_EVALUATED`
- `completed_trial_count: 0`
- null efficacy metrics
- an explicit statement that real before/after data are still required

## Synthetic Verification

Unit tests may create synthetic records in temporary directories to verify
formulas and validation behavior. Synthetic fixtures must not be copied into
`outputs/data/`, counted as E8 evidence, or cited as recommendation efficacy.

