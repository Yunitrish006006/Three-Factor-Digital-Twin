"""Locations and transparent steady heat balance for the corrective review."""
import hashlib
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'openspec/changes/prototype-sparse-enclosure-transfer-20261006/artifacts'
CHANGE = ROOT / 'openspec/changes/correct-sparse-enclosure-review-20261006'
ARTIFACTS = CHANGE / 'artifacts'
REFERENCE_COMMIT = 'ebb40f96731f8956880b8e1ad2921ded8ac8a4ea'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equilibrium(parameters, power, inlet, fan):
    """Thermal steady state for fixed inlet/power/fan; not a trajectory forecast."""
    if not all(math.isfinite(v) for v in (power, inlet, fan)) or not 0 <= fan <= 1:
        raise ValueError('Finite power/inlet and normalized fan required')
    p = parameters
    g, v = p['contact'], p['plate_base'] + p['plate_fan'] * fan
    w, b = p['air_base'] + p['air_fan'] * fan, p['bypass']
    matrix = np.array([[g + b, -g, 0.], [-g, g + v, -v], [0., -v, v + w]])
    return np.linalg.solve(matrix, [power + b * inlet, 0., w * inlet])
