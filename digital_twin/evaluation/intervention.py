from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence


METRICS = ("temperature", "humidity", "illuminance")
CONDITIONS = {
    "top_ranked",
    "no_action",
    "human_baseline",
    "alternative_action",
}
VALID_STATUSES = {"COMPLETED", "EXCLUDED"}
EVIDENCE_CLASSES = {"REAL_INTERVENTION", "SYNTHETIC_TEST"}
CONSISTENCY_TOLERANCE = 1e-4


class InterventionValidationError(ValueError):
    """Raised when an E8 dataset violates the preregistered contract."""


def comfort_penalty(values: Mapping[str, object], target: Mapping[str, object]) -> float:
    """Compute the repository's tolerance-normalized three-factor penalty."""

    total = 0.0
    for metric in METRICS:
        value = _number(values.get(metric), f"values.{metric}")
        target_spec = _mapping(target.get(metric), f"target.{metric}")
        target_value = _number(target_spec.get("value"), f"target.{metric}.value")
        tolerance = _number(
            target_spec.get("tolerance"),
            f"target.{metric}.tolerance",
            positive=True,
        )
        weight = _number(
            target_spec.get("weight"),
            f"target.{metric}.weight",
            nonnegative=True,
        )
        deviation = abs(value - target_value)
        normalized = 0.0 if deviation <= tolerance else (deviation - tolerance) / tolerance
        total += weight * normalized
    return total


def validate_intervention_dataset(dataset: Mapping[str, object]) -> None:
    root = _mapping(dataset, "dataset")
    _reject_unknown_keys(
        root,
        {
            "schema_version",
            "experiment_id",
            "evidence_class",
            "study",
            "trials",
        },
        "dataset",
    )
    _require_exact(root.get("schema_version"), "1.0.0", "schema_version")
    _require_exact(root.get("experiment_id"), "E8", "experiment_id")

    evidence_class = _string(root.get("evidence_class"), "evidence_class")
    if evidence_class not in EVIDENCE_CLASSES:
        raise InterventionValidationError(
            f"evidence_class must be one of {sorted(EVIDENCE_CLASSES)}"
        )

    study = _mapping(root.get("study"), "study")
    _validate_study(study)

    trials = root.get("trials")
    if not isinstance(trials, list):
        raise InterventionValidationError("trials must be an array")

    seen_trial_ids = set()
    for index, raw_trial in enumerate(trials):
        trial = _mapping(raw_trial, f"trials[{index}]")
        trial_id = _string(trial.get("trial_id"), f"trials[{index}].trial_id")
        if trial_id in seen_trial_ids:
            raise InterventionValidationError(f"duplicate trial_id: {trial_id}")
        seen_trial_ids.add(trial_id)
        _validate_trial(trial, study, index)


def analyze_intervention_dataset(dataset: Mapping[str, object]) -> Dict[str, object]:
    validate_intervention_dataset(dataset)
    study = _mapping(dataset["study"], "study")
    trials = list(dataset["trials"])
    completed = [trial for trial in trials if trial["status"] == "COMPLETED"]
    excluded = [trial for trial in trials if trial["status"] == "EXCLUDED"]
    evidence_class = str(dataset["evidence_class"])

    condition_counts = Counter(str(trial["condition"]) for trial in completed)
    trial_results = [_analyze_trial(trial) for trial in completed]
    top_ranked = [
        result for result in trial_results if result["condition"] == "top_ranked"
    ]
    prediction_results = [
        result
        for result in trial_results
        if result["absolute_prediction_error"] is not None
    ]

    direction_values: Dict[str, List[float]] = {metric: [] for metric in METRICS}
    for result in trial_results:
        directions = result["direction_agreement"]
        for metric in METRICS:
            value = directions[metric]
            if value is not None:
                direction_values[metric].append(1.0 if value else 0.0)

    block_metrics = _matched_block_metrics(completed, trial_results)
    has_completed = bool(completed)
    status = (
        "SYNTHETIC_TEST_ONLY"
        if evidence_class == "SYNTHETIC_TEST"
        else ("DESCRIPTIVE_EVIDENCE" if has_completed else "NOT_EVALUATED")
    )

    metrics: Dict[str, object] = {
        "top_ranked_success_rate": _mean_or_none(
            [1.0 if item["actual_improvement"] > 0 else 0.0 for item in top_ranked]
        ),
        "top_ranked_mean_actual_improvement": _mean_or_none(
            [float(item["actual_improvement"]) for item in top_ranked]
        ),
        "mean_absolute_prediction_error": _mean_or_none(
            [
                float(item["absolute_prediction_error"])
                for item in prediction_results
            ]
        ),
        "direction_accuracy": {
            metric: _mean_or_none(direction_values[metric]) for metric in METRICS
        },
        "overall_direction_accuracy": _mean_or_none(
            [value for values in direction_values.values() for value in values]
        ),
        "matched_block_top1_regret_mean": _mean_or_none(
            [item["top1_regret"] for item in block_metrics if item["top1_regret"] is not None]
        ),
        "matched_block_spearman_mean": _mean_or_none(
            [item["spearman"] for item in block_metrics if item["spearman"] is not None]
        ),
        "matched_block_count_top1_regret": sum(
            1 for item in block_metrics if item["top1_regret"] is not None
        ),
        "matched_block_count_rank_correlation": sum(
            1 for item in block_metrics if item["spearman"] is not None
        ),
    }

    if not has_completed:
        metrics = {
            "top_ranked_success_rate": None,
            "top_ranked_mean_actual_improvement": None,
            "mean_absolute_prediction_error": None,
            "direction_accuracy": {metric: None for metric in METRICS},
            "overall_direction_accuracy": None,
            "matched_block_top1_regret_mean": None,
            "matched_block_spearman_mean": None,
            "matched_block_count_top1_regret": 0,
            "matched_block_count_rank_correlation": 0,
        }

    return {
        "schema_version": "1.0.0",
        "experiment_id": "E8",
        "evidence_status": status,
        "source_evidence_class": evidence_class,
        "study_id": study["study_id"],
        "room_id": study["room_id"],
        "target_scope": study["target_scope"],
        "study_status": study["status"],
        "trial_counts": {
            "total": len(trials),
            "completed": len(completed),
            "excluded": len(excluded),
            "by_condition": {
                condition: condition_counts.get(condition, 0)
                for condition in sorted(CONDITIONS)
            },
        },
        "exclusions": [
            {
                "trial_id": trial["trial_id"],
                "reason": trial["exclusion_reason"],
            }
            for trial in excluded
        ],
        "metrics": _round_nested(metrics),
        "matched_blocks": _round_nested(block_metrics),
        "trials": _round_nested(trial_results),
        "claim_boundary": (
            "No completed real before/after intervention trials are available; "
            "recommendation efficacy remains not evaluated."
            if not has_completed
            else (
                "Descriptive E8 intervention evidence only; causal scope depends "
                "on matched controls, protocol adherence, and the registered design."
            )
        ),
    }


def _validate_study(study: Mapping[str, object]) -> None:
    _reject_unknown_keys(
        study,
        {
            "study_id",
            "room_id",
            "target_scope",
            "settling_interval_minutes",
            "planned_conditions",
            "status",
        },
        "study",
    )
    _string(study.get("study_id"), "study.study_id")
    _string(study.get("room_id"), "study.room_id")
    status = _string(study.get("status"), "study.status")
    if status not in {
        "READY_FOR_DATA_COLLECTION",
        "DATA_COLLECTION_IN_PROGRESS",
        "COMPLETE",
    }:
        raise InterventionValidationError(f"unsupported study.status: {status}")

    scope = _mapping(study.get("target_scope"), "study.target_scope")
    _reject_unknown_keys(scope, {"kind", "name", "position_m"}, "study.target_scope")
    _require_exact(scope.get("kind"), "point", "study.target_scope.kind")
    _string(scope.get("name"), "study.target_scope.name")
    position = _mapping(scope.get("position_m"), "study.target_scope.position_m")
    _reject_unknown_keys(
        position,
        {"x", "y", "z"},
        "study.target_scope.position_m",
    )
    for axis in ("x", "y", "z"):
        _number(
            position.get(axis),
            f"study.target_scope.position_m.{axis}",
            nonnegative=True,
        )

    interval = _mapping(
        study.get("settling_interval_minutes"),
        "study.settling_interval_minutes",
    )
    _reject_unknown_keys(
        interval,
        {"minimum", "maximum"},
        "study.settling_interval_minutes",
    )
    minimum = _number(
        interval.get("minimum"),
        "study.settling_interval_minutes.minimum",
        positive=True,
    )
    maximum = _number(
        interval.get("maximum"),
        "study.settling_interval_minutes.maximum",
        positive=True,
    )
    if minimum > maximum:
        raise InterventionValidationError(
            "study settling interval minimum cannot exceed maximum"
        )

    planned = study.get("planned_conditions")
    if not isinstance(planned, list) or not planned:
        raise InterventionValidationError("study.planned_conditions must be non-empty")
    if len(set(planned)) != len(planned):
        raise InterventionValidationError("study.planned_conditions must be unique")
    unsupported = set(planned) - CONDITIONS
    if unsupported:
        raise InterventionValidationError(
            f"unsupported planned conditions: {sorted(unsupported)}"
        )


def _validate_trial(
    trial: Mapping[str, object],
    study: Mapping[str, object],
    index: int,
) -> None:
    prefix = f"trials[{index}]"
    _reject_unknown_keys(
        trial,
        {
            "trial_id",
            "block_id",
            "status",
            "exclusion_reason",
            "condition",
            "started_at",
            "completed_at",
            "target",
            "before",
            "predicted_ranking",
            "executed_action",
            "settling_minutes",
            "after",
            "protocol_deviations",
            "operator_notes",
        },
        prefix,
    )
    _string(trial.get("block_id"), f"{prefix}.block_id")
    status = _string(trial.get("status"), f"{prefix}.status")
    if status not in VALID_STATUSES:
        raise InterventionValidationError(
            f"{prefix}.status must be one of {sorted(VALID_STATUSES)}"
        )
    condition = _string(trial.get("condition"), f"{prefix}.condition")
    if condition not in CONDITIONS:
        raise InterventionValidationError(f"unsupported {prefix}.condition: {condition}")

    started = _datetime(trial.get("started_at"), f"{prefix}.started_at")
    completed = _datetime(trial.get("completed_at"), f"{prefix}.completed_at")
    if completed <= started:
        raise InterventionValidationError(
            f"{prefix}.completed_at must be later than started_at"
        )

    target = _mapping(trial.get("target"), f"{prefix}.target")
    _validate_target(target, f"{prefix}.target")
    before = _mapping(trial.get("before"), f"{prefix}.before")
    after = _mapping(trial.get("after"), f"{prefix}.after")
    _validate_observation(before, f"{prefix}.before")
    _validate_observation(after, f"{prefix}.after")

    ranking = trial.get("predicted_ranking")
    if not isinstance(ranking, list) or not ranking:
        raise InterventionValidationError(
            f"{prefix}.predicted_ranking must be non-empty"
        )
    _validate_ranking(ranking, before, target, prefix)

    executed_action = _string(
        trial.get("executed_action"),
        f"{prefix}.executed_action",
    )
    ranking_by_action = {item["action_name"]: item for item in ranking}
    top_action = min(ranking, key=lambda item: item["rank"])["action_name"]
    if condition == "top_ranked" and executed_action != top_action:
        raise InterventionValidationError(
            f"{prefix} top_ranked trial must execute rank-1 action {top_action}"
        )
    if condition == "alternative_action":
        if executed_action not in ranking_by_action:
            raise InterventionValidationError(
                f"{prefix} alternative action must appear in predicted_ranking"
            )
        if ranking_by_action[executed_action]["rank"] == 1:
            raise InterventionValidationError(
                f"{prefix} alternative action cannot be predicted rank 1"
            )

    settling = _number(
        trial.get("settling_minutes"),
        f"{prefix}.settling_minutes",
        positive=True,
    )
    deviations = trial.get("protocol_deviations")
    if not isinstance(deviations, list) or any(
        not isinstance(item, str) or not item.strip() for item in deviations
    ):
        raise InterventionValidationError(
            f"{prefix}.protocol_deviations must be an array of non-empty strings"
        )
    interval = study["settling_interval_minutes"]
    if not interval["minimum"] <= settling <= interval["maximum"] and not deviations:
        raise InterventionValidationError(
            f"{prefix} settling_minutes is outside the registered interval "
            "without a protocol deviation"
        )

    if status == "EXCLUDED":
        _string(trial.get("exclusion_reason"), f"{prefix}.exclusion_reason")


def _validate_target(target: Mapping[str, object], prefix: str) -> None:
    _reject_unknown_keys(target, set(METRICS), prefix)
    for metric in METRICS:
        spec = _mapping(target.get(metric), f"{prefix}.{metric}")
        _reject_unknown_keys(
            spec,
            {"value", "tolerance", "weight"},
            f"{prefix}.{metric}",
        )
        _number(spec.get("value"), f"{prefix}.{metric}.value")
        _number(
            spec.get("tolerance"),
            f"{prefix}.{metric}.tolerance",
            positive=True,
        )
        _number(
            spec.get("weight"),
            f"{prefix}.{metric}.weight",
            nonnegative=True,
        )


def _validate_observation(observation: Mapping[str, object], prefix: str) -> None:
    _reject_unknown_keys(observation, {"values", "external"}, prefix)
    values = _mapping(observation.get("values"), f"{prefix}.values")
    _reject_unknown_keys(values, set(METRICS), f"{prefix}.values")
    for metric in METRICS:
        _number(
            values.get(metric),
            f"{prefix}.values.{metric}",
            nonnegative=(metric == "illuminance"),
        )
    external = _mapping(observation.get("external"), f"{prefix}.external")
    _reject_unknown_keys(
        external,
        {
            "outdoor_temperature",
            "outdoor_humidity",
            "sunlight_illuminance",
        },
        f"{prefix}.external",
    )
    _number(
        external.get("outdoor_temperature"),
        f"{prefix}.external.outdoor_temperature",
    )
    _number(
        external.get("outdoor_humidity"),
        f"{prefix}.external.outdoor_humidity",
    )
    _number(
        external.get("sunlight_illuminance"),
        f"{prefix}.external.sunlight_illuminance",
        nonnegative=True,
    )


def _validate_ranking(
    ranking: Sequence[Mapping[str, object]],
    before: Mapping[str, object],
    target: Mapping[str, object],
    prefix: str,
) -> None:
    ranks = []
    action_names = []
    before_penalty = comfort_penalty(before["values"], target)
    for rank_index, raw_item in enumerate(ranking):
        item = _mapping(
            raw_item,
            f"{prefix}.predicted_ranking[{rank_index}]",
        )
        _reject_unknown_keys(
            item,
            {
                "rank",
                "action_name",
                "predicted_after",
                "predicted_penalty",
                "predicted_improvement",
            },
            f"{prefix}.predicted_ranking[{rank_index}]",
        )
        rank = item.get("rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise InterventionValidationError(
                f"{prefix}.predicted_ranking[{rank_index}].rank must be a positive integer"
            )
        action_name = _string(
            item.get("action_name"),
            f"{prefix}.predicted_ranking[{rank_index}].action_name",
        )
        predicted_after = _mapping(
            item.get("predicted_after"),
            f"{prefix}.predicted_ranking[{rank_index}].predicted_after",
        )
        _reject_unknown_keys(
            predicted_after,
            set(METRICS),
            f"{prefix}.predicted_ranking[{rank_index}].predicted_after",
        )
        for metric in METRICS:
            _number(
                predicted_after.get(metric),
                f"{prefix}.predicted_ranking[{rank_index}].predicted_after.{metric}",
                nonnegative=(metric == "illuminance"),
            )
        predicted_penalty = _number(
            item.get("predicted_penalty"),
            f"{prefix}.predicted_ranking[{rank_index}].predicted_penalty",
            nonnegative=True,
        )
        predicted_improvement = _number(
            item.get("predicted_improvement"),
            f"{prefix}.predicted_ranking[{rank_index}].predicted_improvement",
        )
        computed_penalty = comfort_penalty(predicted_after, target)
        computed_improvement = before_penalty - computed_penalty
        _require_close(
            predicted_penalty,
            computed_penalty,
            f"{prefix}.predicted_ranking[{rank_index}].predicted_penalty",
        )
        _require_close(
            predicted_improvement,
            computed_improvement,
            f"{prefix}.predicted_ranking[{rank_index}].predicted_improvement",
        )
        ranks.append(rank)
        action_names.append(action_name)

    if sorted(ranks) != list(range(1, len(ranking) + 1)):
        raise InterventionValidationError(
            f"{prefix}.predicted_ranking ranks must be consecutive from 1"
        )
    if len(set(action_names)) != len(action_names):
        raise InterventionValidationError(
            f"{prefix}.predicted_ranking action names must be unique"
        )


def _analyze_trial(trial: Mapping[str, object]) -> Dict[str, object]:
    target = trial["target"]
    before_values = trial["before"]["values"]
    after_values = trial["after"]["values"]
    before_penalty = comfort_penalty(before_values, target)
    after_penalty = comfort_penalty(after_values, target)
    actual_improvement = before_penalty - after_penalty

    prediction = next(
        (
            item
            for item in trial["predicted_ranking"]
            if item["action_name"] == trial["executed_action"]
        ),
        None,
    )
    predicted_improvement = (
        float(prediction["predicted_improvement"]) if prediction is not None else None
    )
    prediction_error = (
        abs(predicted_improvement - actual_improvement)
        if predicted_improvement is not None
        else None
    )
    directions = {
        metric: _direction_agreement(
            before=float(before_values[metric]),
            predicted=(
                float(prediction["predicted_after"][metric])
                if prediction is not None
                else None
            ),
            measured=float(after_values[metric]),
        )
        for metric in METRICS
    }
    return {
        "trial_id": trial["trial_id"],
        "block_id": trial["block_id"],
        "condition": trial["condition"],
        "executed_action": trial["executed_action"],
        "settling_minutes": trial["settling_minutes"],
        "penalty_before": before_penalty,
        "penalty_after": after_penalty,
        "actual_improvement": actual_improvement,
        "predicted_improvement": predicted_improvement,
        "absolute_prediction_error": prediction_error,
        "direction_agreement": directions,
        "protocol_deviation_count": len(trial["protocol_deviations"]),
    }


def _matched_block_metrics(
    trials: Sequence[Mapping[str, object]],
    trial_results: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    result_by_trial = {item["trial_id"]: item for item in trial_results}
    blocks: MutableMapping[str, List[Mapping[str, object]]] = defaultdict(list)
    for trial in trials:
        blocks[str(trial["block_id"])].append(trial)

    output = []
    for block_id in sorted(blocks):
        block_trials = blocks[block_id]
        top_trials = [
            trial for trial in block_trials if trial["condition"] == "top_ranked"
        ]
        actual_by_action = {
            str(trial["executed_action"]): float(
                result_by_trial[str(trial["trial_id"])]["actual_improvement"]
            )
            for trial in block_trials
        }
        top1_regret = None
        spearman = None
        if len(top_trials) == 1 and len(actual_by_action) >= 2:
            top_trial = top_trials[0]
            top_actual = actual_by_action[str(top_trial["executed_action"])]
            top1_regret = max(actual_by_action.values()) - top_actual

            predicted_ranks = {
                str(item["action_name"]): float(item["rank"])
                for item in top_trial["predicted_ranking"]
            }
            comparable = sorted(set(predicted_ranks) & set(actual_by_action))
            if len(comparable) >= 2:
                actual_ranks = _descending_average_ranks(
                    {action: actual_by_action[action] for action in comparable}
                )
                spearman = _pearson(
                    [predicted_ranks[action] for action in comparable],
                    [actual_ranks[action] for action in comparable],
                )

        output.append(
            {
                "block_id": block_id,
                "completed_action_arm_count": len(actual_by_action),
                "top1_regret": top1_regret,
                "spearman": spearman,
            }
        )
    return output


def _descending_average_ranks(values: Mapping[str, float]) -> Dict[str, float]:
    grouped: MutableMapping[float, List[str]] = defaultdict(list)
    for name, value in values.items():
        grouped[value].append(name)
    ranks: Dict[str, float] = {}
    cursor = 1
    for value in sorted(grouped, reverse=True):
        names = sorted(grouped[value])
        average_rank = (cursor + cursor + len(names) - 1) / 2.0
        for name in names:
            ranks[name] = average_rank
        cursor += len(names)
    return ranks


def _pearson(left: Sequence[float], right: Sequence[float]) -> Optional[float]:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum(
        (x - left_mean) * (y - right_mean) for x, y in zip(left, right)
    )
    left_scale = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_scale = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if left_scale == 0.0 or right_scale == 0.0:
        return None
    return numerator / (left_scale * right_scale)


def _direction_agreement(
    before: float,
    predicted: Optional[float],
    measured: float,
) -> Optional[bool]:
    if predicted is None:
        return None
    predicted_change = predicted - before
    measured_change = measured - before
    if abs(predicted_change) <= 1e-12:
        return None
    return _sign(predicted_change) == _sign(measured_change)


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _mean_or_none(values: Iterable[float]) -> Optional[float]:
    collected = list(values)
    return mean(collected) if collected else None


def _round_nested(value: object) -> object:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [_round_nested(item) for item in value]
    if isinstance(value, dict):
        return {key: _round_nested(item) for key, item in value.items()}
    return value


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise InterventionValidationError(f"{path} must be an object")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InterventionValidationError(f"{path} must be a non-empty string")
    return value


def _number(
    value: object,
    path: str,
    *,
    positive: bool = False,
    nonnegative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InterventionValidationError(f"{path} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise InterventionValidationError(f"{path} must be finite")
    if positive and result <= 0:
        raise InterventionValidationError(f"{path} must be greater than zero")
    if nonnegative and result < 0:
        raise InterventionValidationError(f"{path} must be nonnegative")
    return result


def _datetime(value: object, path: str) -> datetime:
    text = _string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InterventionValidationError(
            f"{path} must be an ISO-8601 date-time"
        ) from exc
    if parsed.tzinfo is None:
        raise InterventionValidationError(f"{path} must include a timezone")
    return parsed


def _require_exact(value: object, expected: object, path: str) -> None:
    if value != expected:
        raise InterventionValidationError(f"{path} must equal {expected!r}")


def _require_close(actual: float, expected: float, path: str) -> None:
    if not math.isclose(
        actual,
        expected,
        abs_tol=CONSISTENCY_TOLERANCE,
        rel_tol=CONSISTENCY_TOLERANCE,
    ):
        raise InterventionValidationError(
            f"{path}={actual} is inconsistent with computed value {expected}"
        )


def _reject_unknown_keys(
    value: Mapping[str, object],
    allowed: set,
    path: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InterventionValidationError(
            f"{path} contains unsupported fields: {unknown}"
        )
