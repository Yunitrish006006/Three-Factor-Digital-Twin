#!/usr/bin/env python3
"""Run the preregistered E14C corrected-data retrospective sensitivity."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.enclosure.bmc_virtual_sensor import (
    evaluate_frozen,
    parse_influx_bmc,
    predict,
    select_and_refit,
)


EXPECTED_MANIFEST_SHA256 = "9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74"
EXPECTED_E14B_SHA256 = "db1525cf0dc11d5c84342415e3658f6905ef27e379b2be85c56fe5f914dd7ef4"
MANIFEST = Path("outputs/data/enclosure/bmc_cross_run_e12_manifest.json")
E14B_RESULT = Path("outputs/data/enclosure/bmc_unit_regimes_e14b_result.json")
RAW_DIR = Path("outputs/data/enclosure/bmc_cross_run_e12/raw")
FROZEN = Path("outputs/data/enclosure/bmc_corrected_e14c_frozen_model.json")
RESULT = Path("outputs/data/enclosure/bmc_corrected_e14c_result.json")
MIN_VALID_ROWS = 10


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if sha256_path(MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("E14C manifest hash mismatch")
    if sha256_path(E14B_RESULT) != EXPECTED_E14B_SHA256:
        raise RuntimeError("E14C E14B-result hash mismatch")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = {"train": [], "selection": [], "test": []}
    for item in manifest["files"]:
        items[item["split"]].append(item)
    parse_report = {}

    def load_split(split: str) -> dict[str, list[dict]]:
        loaded = {}
        for item in items[split]:
            path = RAW_DIR / item["filename"]
            if path.stat().st_size != item["bytes"] or sha256_path(path) != item["sha256"]:
                raise RuntimeError(f"frozen source mismatch: {item['filename']}")
            parsed = parse_influx_bmc(path)
            if len(parsed["rows"]) < MIN_VALID_ROWS:
                raise RuntimeError(f"insufficient corrected rows: {item['filename']}")
            if not all(section["concordant"] for section in parsed["unit_sections"]):
                raise RuntimeError(f"discordant unit section: {item['filename']}")
            loaded[item["filename"]] = parsed["rows"]
            parse_report[item["filename"]] = {
                "split": split,
                "valid_rows": len(parsed["rows"]),
                "unit_sections": parsed["unit_sections"],
            }
        return loaded

    train_runs = load_split("train")
    selection_runs = load_split("selection")
    development = select_and_refit(train_runs, selection_runs)
    frozen_record = {
        "study_id": "E14C",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "e14b_result_sha256": EXPECTED_E14B_SHA256,
        "created_before_retrospective_test_load": True,
        "retrospective_test_filenames": [item["filename"] for item in items["test"]],
        **development,
    }
    FROZEN.write_text(
        json.dumps(frozen_record, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    frozen_sha256 = sha256_path(FROZEN)

    test_runs = load_split("test")
    final = evaluate_frozen(frozen_record["frozen_models"], test_runs)
    final.pop("decision", None)
    prediction_extrema = {}
    for name, model in frozen_record["frozen_models"].items():
        values = [
            predict(model, row)
            for rows in test_runs.values()
            for row in rows
        ]
        prediction_extrema[name] = {
            "count": len(values),
            "min_c": min(values),
            "max_c": max(values),
            "all_finite": all(math.isfinite(value) for value in values),
            "all_in_minus50_200_c": all(-50.0 <= value <= 200.0 for value in values),
        }
    eligibility_gates = {
        **final["gates"],
        "baseline_predictions_plausible": (
            prediction_extrema["baseline"]["all_finite"]
            and prediction_extrema["baseline"]["all_in_minus50_200_c"]
        ),
        "ridge_predictions_plausible": (
            prediction_extrema["ridge"]["all_finite"]
            and prediction_extrema["ridge"]["all_in_minus50_200_c"]
        ),
    }
    eligibility = (
        "candidate_eligible_for_new_confirmation"
        if all(eligibility_gates.values())
        else "candidate_not_eligible_for_confirmation"
    )
    result = {
        "study_id": "E14C",
        "status": "completed_retrospective_sensitivity",
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "e14b_result_sha256": EXPECTED_E14B_SHA256,
        "frozen_model_sha256": frozen_sha256,
        "retrospective_test_previously_opened": True,
        "split_file_counts": {key: len(value) for key, value in items.items()},
        "parse_report": parse_report,
        "development": development,
        "retrospective_test": final["test"],
        "original_accuracy_gates": final["gates"],
        "prediction_extrema": prediction_extrema,
        "eligibility_gates": eligibility_gates,
        "eligibility_decision": eligibility,
        "claim_boundary": (
            "Retrospective candidate eligibility only; not unseen confirmation or "
            "physical, spatial, causal, cross-server, PC-chassis, or NTC evidence."
        ),
    }
    RESULT.write_text(
        json.dumps(result, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "eligibility_decision": eligibility,
        "selected_baseline": development["selection"]["selected_baseline_source"],
        "selected_feature_set": development["selection"]["selected_feature_set"],
        "selected_ridge_lambda": development["selection"]["selected_ridge_lambda"],
        "baseline_test": final["test"]["baseline"]["pooled"],
        "ridge_test": final["test"]["model"]["pooled"],
        "wins": final["test"]["model_run_wins"],
        "ci": final["test"]["run_bootstrap_95_ci_c"],
        "prediction_extrema": prediction_extrema,
        "eligibility_gates": eligibility_gates,
    }, indent=2))


if __name__ == "__main__":
    main()
