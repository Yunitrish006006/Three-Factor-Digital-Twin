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

# Optional scientific dependencies are loaded only when the temperature-session
# API is requested; public BMC parsing remains usable without SciPy.
def __getattr__(name):
    if name in ('EnclosureSession', 'Observation', 'fit_observations'):
        from digital_twin.enclosure import session
        return getattr(session, name)
    raise AttributeError(name)

__all__ += ['EnclosureSession', 'Observation', 'fit_observations']
