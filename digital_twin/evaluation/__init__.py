"""Evaluation helpers for research evidence pipelines."""

from digital_twin.evaluation.intervention import (
    InterventionValidationError,
    analyze_intervention_dataset,
    comfort_penalty,
    validate_intervention_dataset,
)
from digital_twin.evaluation.published_hybrid_comparison import (
    run_oh2024_inspired_comparison,
    write_oh2024_inspired_comparison,
)
from digital_twin.evaluation.next_day_temperature_comparison import (
    run_next_day_temperature_comparison,
    write_next_day_temperature_comparison,
)
from digital_twin.evaluation.rnn_public_comparison import (
    RNNConfig,
    VanillaElmanRNN,
    run_rnn_public_comparison,
    write_rnn_public_comparison,
)

__all__ = [
    "InterventionValidationError",
    "analyze_intervention_dataset",
    "comfort_penalty",
    "validate_intervention_dataset",
    "run_oh2024_inspired_comparison",
    "write_oh2024_inspired_comparison",
    "run_next_day_temperature_comparison",
    "write_next_day_temperature_comparison",
    "RNNConfig",
    "VanillaElmanRNN",
    "run_rnn_public_comparison",
    "write_rnn_public_comparison",
]
