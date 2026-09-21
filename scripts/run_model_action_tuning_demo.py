#!/usr/bin/env python3
"""Concrete dry-run showing how the thesis DigitalTwinModel ranks actions.

The validation scenario and observations are synthetic fixtures from the
repository.  This demonstrates the tuning/action-ranking mechanics only; it
is not a new physical or causal experiment.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from digital_twin.core.demo import synthesize_sensor_observations
from digital_twin.core.entities import Action, ActionEffect
from digital_twin.core.scenarios import apply_truth_adjustments, build_validation_scenarios
from digital_twin.physics.model import DigitalTwinModel
from digital_twin.physics.recommendations import rank_actions, score_zone

OUT = ROOT / "openspec/changes/systematic-parameter-tuning-20260921/artifacts/model_action_tuning_demo.json"


def main() -> None:
    scenario = build_validation_scenarios()[0]
    model = DigitalTwinModel()
    truth = model.simulate(
        scenario.room, scenario.environment,
        apply_truth_adjustments(scenario.devices, scenario.truth_adjustments),
        scenario.furniture, scenario.sensors, scenario.zones,
        scenario.elapsed_minutes, scenario.resolution,
    )
    observed = synthesize_sensor_observations(truth.sensor_predictions, scenario.sensors)
    baseline = model.simulate(
        scenario.room, scenario.environment, scenario.devices,
        scenario.furniture, scenario.sensors, scenario.zones,
        scenario.elapsed_minutes, scenario.resolution,
        observed_sensors=observed,
    )
    actions = [
        Action(f"ac_{level:.2f}", f"AC activation {level:.0%}", [ActionEffect("ac_main", activation=level)])
        for level in (0.35, 0.60, 0.85)
    ]
    ranked = rank_actions(
        model, scenario.room, scenario.environment, scenario.devices,
        scenario.furniture, scenario.sensors, scenario.zones,
        scenario.target_zone_name, scenario.comfort_target, actions,
        scenario.elapsed_minutes, scenario.resolution, observed,
    )
    artifact = {
        "status": "DEMO_MODEL_NATIVE_ACTION_RANKING_NOT_CONTROL_EVIDENCE",
        "scenario": scenario.name,
        "target_zone": scenario.target_zone_name,
        "target": {
            "temperature_C": scenario.comfort_target.temperature,
            "humidity_pct": scenario.comfort_target.humidity,
            "illuminance_lux": scenario.comfort_target.illuminance,
        },
        "calibration_inputs": {"observed_sensor_count": len(observed), "model": "DigitalTwinModel"},
        "candidate_actions": [0.35, 0.60, 0.85],
        "baseline_zone": baseline.zone_averages[scenario.target_zone_name],
        "ranked_actions": [
            {
                "name": item.name,
                "improvement": item.improvement,
                "resulting_zone_values": item.resulting_zone_values,
                "resulting_penalty": item.resulting_penalty,
            }
            for item in ranked
        ],
        "next_step": "Execute the top-ranked action through a real actuator/simulator, then compare observed post-action temperature with this predicted zone value.",
        "boundary": "Synthetic repository validation fixture; static model ranking only, not hardware, BOPTEST, or causal intervention evidence.",
    }
    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "top_action": ranked[0].name, "ranked_actions": artifact["ranked_actions"], "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
