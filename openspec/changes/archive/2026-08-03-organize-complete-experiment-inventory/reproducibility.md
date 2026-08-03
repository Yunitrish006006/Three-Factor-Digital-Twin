# Reproducibility

## Primary Inputs

- `outputs/data/validation_summary.json`
- `outputs/data/submission_readiness_summary.json`
- `outputs/data/window_matrix_summary.json`
- `outputs/data/hybrid_residual_summary.json`
- `outputs/data/bedroom_01_weekly/weekly_simulation_summary.json`
- `outputs/data/e8_intervention_summary.json`
- `outputs/data/public_benchmarks/*.json`
- `outputs/data/thesis_result_verification_report.json`

## Producer Commands

| Scope | Command |
| --- | --- |
| E1/E2/E4 | `python3 scripts/run_demo.py` |
| E3/E6 robustness | `python3 scripts/run_submission_readiness_experiments.py` |
| E5 | `python3 scripts/run_window_matrix.py` |
| E6 default | `python3 scripts/run_hybrid_residual_experiment.py` |
| E7 | `python3 scripts/run_bedroom_weekly_simulation.py` |
| E8 | `python3 scripts/analyze_e8_intervention_trials.py` |
| E9 baseline/project | `python3 scripts/run_public_dataset_benchmark.py` and `python3 scripts/run_public_dataset_model_comparison.py` |
| E9 transfer | `python3 scripts/run_oh2024_inspired_comparison.py` |
| E9 next day | `python3 scripts/run_next_day_temperature_comparison.py` |
| E9 RNN | `python3 scripts/run_rnn_public_comparison.py` |

## Environment and Ordering

- Use repository Python 3.9+.
- Preserve registered seeds and chronological splits.
- Reconciliation reads existing outputs first; it does not change configurations.
- After source edits, execute the synchronized rebuild commands from `AGENTS.md` and verify outputs.

