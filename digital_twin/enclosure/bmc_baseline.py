from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from digital_twin.core.math_utils import solve_linear_system


DATASET_NAME = "arealuser/bmcdata"
DATASET_URL = "https://github.com/arealuser/bmcdata"
DATASET_LICENSE = "MIT"
DOMAIN_MIN_C = 20.0
DOMAIN_MAX_C = 30.0
MIN_EXAMPLES = 30
RIDGE = 1e-3

TIME_ALIASES = ("_time", "time", "timestamp")
DEVICE_ALIASES = ("device_id", "device", "host")
INLET_ALIASES = ("Inlet_Temp", "inlet_temperature", "inlet_temp")
OUTLET_ALIASES = ("Outlet_Temp", "IO_Outlet_Temp", "outlet_temperature", "outlet_temp")
POWER_FIELDS = ("PSU1_Total_Power", "PSU2_Total_Power", "Total_Power", "power")
FAN_FIELDS = ("FAN1", "FAN2", "FAN3", "FAN4", "PSU1_FAN", "PSU2_FAN", "fan_speed")
METHODS = ("persistence", "linear_readout", "thermal_balance_readout")


@dataclass(frozen=True)
class BMCObservation:
    timestamp: datetime
    device_id: str
    inlet_temperature_c: float
    outlet_temperature_c: float
    total_power_w: float
    mean_fan_rpm: float


@dataclass(frozen=True)
class _Example:
    current: BMCObservation
    target: BMCObservation


@dataclass(frozen=True)
class _LinearModel:
    means: Tuple[float, ...]
    scales: Tuple[float, ...]
    coefficients: Tuple[float, ...]

    def predict(self, features: Sequence[float]) -> float:
        standardized = [
            (float(value) - self.means[index]) / self.scales[index]
            for index, value in enumerate(features)
        ]
        return self.coefficients[0] + sum(
            weight * value
            for weight, value in zip(self.coefficients[1:], standardized)
        )


def _normalized_row(row: Mapping[str, object]) -> Dict[str, object]:
    return {str(key).strip().lower(): value for key, value in row.items() if key is not None}


def _value(row: Mapping[str, object], aliases: Iterable[str]) -> Optional[object]:
    normalized = _normalized_row(row)
    for alias in aliases:
        candidate = normalized.get(alias.lower())
        if candidate is not None and str(candidate).strip() != "":
            return candidate
    return None


def _finite_float(value: object) -> Optional[float]:
    try:
        result = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _parse_timestamp(value: object) -> Optional[datetime]:
    raw = str(value).strip()
    if not raw or raw.lower() in {"_time", "time", "timestamp"}:
        return None
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sum_available(row: Mapping[str, object], fields: Sequence[str]) -> Optional[float]:
    values = [
        parsed
        for field in fields
        for parsed in [_finite_float(_value(row, (field,)))]
        if parsed is not None
    ]
    return sum(values) if values else None


def _mean_available(row: Mapping[str, object], fields: Sequence[str]) -> Optional[float]:
    values = [
        parsed
        for field in fields
        for parsed in [_finite_float(_value(row, (field,)))]
        if parsed is not None
    ]
    return sum(values) / float(len(values)) if values else None


def load_bmc_observations(path: Path) -> Tuple[List[BMCObservation], Dict[str, int]]:
    source = Path(path)
    counts = {"raw_rows": 0, "parsed_rows": 0, "missing_required_rows": 0}
    observations: List[BMCObservation] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        data_lines = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(data_lines)
        for row in reader:
            counts["raw_rows"] += 1
            timestamp = _parse_timestamp(_value(row, TIME_ALIASES))
            inlet = _finite_float(_value(row, INLET_ALIASES))
            outlet = _finite_float(_value(row, OUTLET_ALIASES))
            power = _sum_available(row, POWER_FIELDS)
            fan = _mean_available(row, FAN_FIELDS)
            if timestamp is None or inlet is None or outlet is None or power is None or fan is None:
                counts["missing_required_rows"] += 1
                continue
            device_value = _value(row, DEVICE_ALIASES)
            observations.append(
                BMCObservation(
                    timestamp=timestamp,
                    device_id=str(device_value).strip() if device_value is not None else "unknown",
                    inlet_temperature_c=inlet,
                    outlet_temperature_c=outlet,
                    total_power_w=power,
                    mean_fan_rpm=fan,
                )
            )
            counts["parsed_rows"] += 1
    observations.sort(key=lambda item: (item.device_id, item.timestamp))
    return observations, counts


def _in_domain(observation: BMCObservation) -> bool:
    return (
        DOMAIN_MIN_C <= observation.inlet_temperature_c <= DOMAIN_MAX_C
        and DOMAIN_MIN_C <= observation.outlet_temperature_c <= DOMAIN_MAX_C
    )


def _build_examples(observations: Sequence[BMCObservation]) -> Tuple[List[_Example], Dict[str, float]]:
    positive_gaps = [
        (right.timestamp - left.timestamp).total_seconds()
        for left, right in zip(observations, observations[1:])
        if left.device_id == right.device_id and right.timestamp > left.timestamp
    ]
    median_cadence = float(median(positive_gaps)) if positive_gaps else 0.0
    max_gap = 3.0 * median_cadence if median_cadence > 0.0 else 0.0
    examples: List[_Example] = []
    nonpositive_gaps = 0
    excessive_gaps = 0
    out_of_domain = 0
    for current, target in zip(observations, observations[1:]):
        if current.device_id != target.device_id:
            continue
        gap = (target.timestamp - current.timestamp).total_seconds()
        if gap <= 0.0:
            nonpositive_gaps += 1
            continue
        if max_gap > 0.0 and gap > max_gap:
            excessive_gaps += 1
            continue
        if not _in_domain(current) or not _in_domain(target):
            out_of_domain += 1
            continue
        examples.append(_Example(current=current, target=target))
    return examples, {
        "median_cadence_seconds": median_cadence,
        "nonpositive_gap_pairs": nonpositive_gaps,
        "excessive_gap_pairs": excessive_gaps,
        "out_of_domain_pairs": out_of_domain,
    }


def _fit_linear_model(features: Sequence[Sequence[float]], targets: Sequence[float]) -> _LinearModel:
    width = len(features[0])
    means = tuple(sum(row[index] for row in features) / float(len(features)) for index in range(width))
    scales = tuple(
        max(
            math.sqrt(sum((row[index] - means[index]) ** 2 for row in features) / float(len(features))),
            1e-6,
        )
        for index in range(width)
    )
    rows = [
        [1.0] + [(float(value) - means[index]) / scales[index] for index, value in enumerate(row)]
        for row in features
    ]
    normal_matrix = [[0.0 for _ in range(width + 1)] for _ in range(width + 1)]
    normal_vector = [0.0 for _ in range(width + 1)]
    for row, target in zip(rows, targets):
        for row_index in range(width + 1):
            normal_vector[row_index] += row[row_index] * float(target)
            for column_index in range(width + 1):
                normal_matrix[row_index][column_index] += row[row_index] * row[column_index]
    for index in range(width + 1):
        normal_matrix[index][index] += RIDGE
    return _LinearModel(means, scales, tuple(solve_linear_system(normal_matrix, normal_vector)))


def _linear_features(example: _Example) -> List[float]:
    current = example.current
    return [
        current.inlet_temperature_c,
        current.outlet_temperature_c,
        current.total_power_w,
        current.mean_fan_rpm,
    ]


def _thermal_features(example: _Example) -> List[float]:
    current = example.current
    temperature_difference = current.inlet_temperature_c - current.outlet_temperature_c
    return [
        temperature_difference,
        current.total_power_w,
        current.mean_fan_rpm * temperature_difference,
    ]


def _metrics(actual: Sequence[float], predicted: Sequence[float]) -> Dict[str, float]:
    if not actual:
        return {"mae": 0.0, "rmse": 0.0}
    errors = [truth - estimate for truth, estimate in zip(actual, predicted)]
    return {
        "mae": round(sum(abs(error) for error in errors) / float(len(errors)), 6),
        "rmse": round(math.sqrt(sum(error * error for error in errors) / float(len(errors))), 6),
    }


def _endpoint_hash(examples: Sequence[_Example]) -> str:
    payload = "\n".join(
        f"{item.current.device_id}|{item.current.timestamp.isoformat()}|{item.target.timestamp.isoformat()}"
        for item in examples
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _predictions(
    examples: Sequence[_Example],
    linear_model: _LinearModel,
    thermal_model: _LinearModel,
) -> Dict[str, List[float]]:
    return {
        "persistence": [item.current.outlet_temperature_c for item in examples],
        "linear_readout": [linear_model.predict(_linear_features(item)) for item in examples],
        "thermal_balance_readout": [
            item.current.outlet_temperature_c + thermal_model.predict(_thermal_features(item))
            for item in examples
        ],
    }


def _evaluate_case(
    source: Path,
    source_hash: str,
    device_id: str,
    observations: Sequence[BMCObservation],
    parse_counts: Mapping[str, int],
) -> Dict[str, object]:
    examples, exclusions = _build_examples(observations)
    retained_ratio = len(examples) / float(max(len(observations) - 1, 1))
    base: Dict[str, object] = {
        "case_id": f"{source.name}:{device_id}",
        "source_file": str(source),
        "source_sha256": source_hash,
        "device_id": device_id,
        "observation_count": len(observations),
        "eligible_example_count": len(examples),
        "eligible_pair_ratio": round(retained_ratio, 6),
        "parse_counts": dict(parse_counts),
        "exclusions": exclusions,
    }
    if len(examples) < MIN_EXAMPLES:
        base.update({"status": "insufficient_in_scope_samples", "minimum_examples": MIN_EXAMPLES})
        return base

    train_end = int(len(examples) * 0.6)
    validation_end = train_end + int(len(examples) * 0.2)
    train = examples[:train_end]
    validation = examples[train_end:validation_end]
    test = examples[validation_end:]
    linear_model = _fit_linear_model(
        [_linear_features(item) for item in train],
        [item.target.outlet_temperature_c for item in train],
    )
    thermal_model = _fit_linear_model(
        [_thermal_features(item) for item in train],
        [item.target.outlet_temperature_c - item.current.outlet_temperature_c for item in train],
    )
    split_metrics: Dict[str, Dict[str, Dict[str, float]]] = {}
    for split_name, split_examples in (("validation", validation), ("test", test)):
        actual = [item.target.outlet_temperature_c for item in split_examples]
        predictions = _predictions(split_examples, linear_model, thermal_model)
        split_metrics[split_name] = {
            method: _metrics(actual, predictions[method])
            for method in METHODS
        }
    winner = min(METHODS, key=lambda method: split_metrics["test"][method]["mae"])
    base.update(
        {
            "status": "ok",
            "split": {
                "train_examples": len(train),
                "validation_examples": len(validation),
                "test_examples": len(test),
                "train_endpoint_hash": _endpoint_hash(train),
                "validation_endpoint_hash": _endpoint_hash(validation),
                "test_endpoint_hash": _endpoint_hash(test),
            },
            "metrics": split_metrics,
            "lowest_test_mae_method": winner,
            "thermal_balance_beats_persistence": (
                split_metrics["test"]["thermal_balance_readout"]["mae"]
                < split_metrics["test"]["persistence"]["mae"]
            ),
        }
    )
    return base


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_bmc_paths(paths: Sequence[Path]) -> Dict[str, object]:
    cases: List[Dict[str, object]] = []
    for raw_path in paths:
        source = Path(raw_path)
        observations, parse_counts = load_bmc_observations(source)
        source_hash = _sha256(source)
        device_ids = sorted({item.device_id for item in observations}) or ["unknown"]
        for device_id in device_ids:
            device_observations = [item for item in observations if item.device_id == device_id]
            cases.append(
                _evaluate_case(
                    source=source,
                    source_hash=source_hash,
                    device_id=device_id,
                    observations=device_observations,
                    parse_counts=parse_counts,
                )
            )
    evaluated = [case for case in cases if case["status"] == "ok"]
    thermal_wins = sum(bool(case["thermal_balance_beats_persistence"]) for case in evaluated)
    lowest_counts = {
        method: sum(case.get("lowest_test_mae_method") == method for case in evaluated)
        for method in METHODS
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": DATASET_NAME,
            "url": DATASET_URL,
            "license": DATASET_LICENSE,
            "source_files_committed": False,
        },
        "protocol": {
            "experiment_id": "E11A",
            "target": "next_valid_outlet_temperature_c",
            "temperature_domain_c": [DOMAIN_MIN_C, DOMAIN_MAX_C],
            "split": "chronological_60_20_20_per_file_and_device",
            "ridge": RIDGE,
            "minimum_examples_per_case": MIN_EXAMPLES,
            "methods": list(METHODS),
            "evidence_class": "public_task_aligned",
        },
        "cases": cases,
        "summary": {
            "status": "ok" if evaluated else "not_evaluated",
            "case_count": len(cases),
            "evaluated_case_count": len(evaluated),
            "thermal_balance_wins_vs_persistence": thermal_wins,
            "thermal_balance_majority_threshold_met": (
                len(evaluated) >= 3 and thermal_wins > len(evaluated) / 2.0
            ),
            "lowest_test_mae_counts": lowest_counts,
        },
    }


def write_bmc_summary(summary: Mapping[str, object], output_path: Path) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
