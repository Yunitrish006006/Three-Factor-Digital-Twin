"""Equipment-enclosure transfer experiments.

This package is intentionally separate from the validated room estimator. Its
outputs support only the evidence class declared by the active enclosure
OpenSpec change.
"""

from digital_twin.enclosure.bmc_baseline import (
    BMCObservation,
    evaluate_bmc_paths,
    load_bmc_observations,
    write_bmc_summary,
)

__all__ = [
    "BMCObservation",
    "evaluate_bmc_paths",
    "load_bmc_observations",
    "write_bmc_summary",
]
