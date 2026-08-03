# Design

## Components

1. `docs/requirements/e8_intervention_trial_schema.json`
   - JSON Schema for study metadata and intervention trials.
2. `docs/templates/e8_intervention_trials_template.json`
   - Empty, field-ready dataset carrying the current E8 design.
3. `digital_twin/evaluation/intervention.py`
   - Validation, comfort-penalty, trial-endpoint, and matched-block analysis.
4. `scripts/analyze_e8_intervention_trials.py`
   - Command-line entrypoint and deterministic JSON/Markdown output.
5. `tests/test_intervention_evaluation.py`
   - Synthetic formula, status, rejection, and matched-block tests.

## Status Semantics

- `NOT_EVALUATED`: no valid completed real trials.
- `DESCRIPTIVE_EVIDENCE`: at least one valid completed real trial; summaries
  remain descriptive unless the registered design supports stronger inference.

The analyzer never upgrades the manuscript claim automatically. Any causal
claim still requires evidence review and a separate completed OpenSpec change.

## Metric Semantics

Comfort penalty reuses the repository's three-factor tolerance-normalized score.
Direction agreement compares the sign of predicted and measured per-factor
changes. Zero predicted changes are reported as unavailable for direction
accuracy. Matched-block rank statistics require at least two comparable action
arms.

