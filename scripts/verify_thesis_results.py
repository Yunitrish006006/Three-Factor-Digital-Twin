from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "data"
REPORT_JSON = DATA / "thesis_result_verification_report.json"
REPORT_MD = DATA / "thesis_result_verification_report.md"

THESIS_SOURCES = [
    ROOT / "docs" / "thesis" / "thesis_draft_zh.md",
    ROOT / "docs" / "papers" / "thesis" / "thesis_draft_zh.tex",
    ROOT / "docs" / "papers" / "ieee" / "paper.tex",
    ROOT / "scripts" / "build_thesis_docx.py",
]

METRICS = ("temperature", "humidity", "illuminance")


@dataclass(frozen=True)
class ResultSpec:
    result_name: str
    thesis_value: float
    evidence_file: Path
    compute: Callable[[], float]
    tolerance: float
    thesis_patterns: Sequence[str]
    suggested_script: str
    category: str
    needs_public_data: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify thesis result numbers against reproducible output JSON.")
    parser.add_argument("--tolerance", type=float, default=None, help="Override all per-result tolerances.")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    specs = _build_specs(args.tolerance)
    results = [_evaluate_spec(spec) for spec in specs]
    summary = _summarize(results)
    report = {
        "summary": summary,
        "source_files_checked": [str(path.relative_to(ROOT)) for path in THESIS_SOURCES],
        "results": results,
        "status_definitions": {
            "PASS": "The thesis value appears in at least one checked source file and matches computed evidence within tolerance.",
            "FAIL": "The thesis value appears in source files, evidence exists, but the computed value differs beyond tolerance.",
            "MISSING": "The thesis value or evidence is missing, so the claim is not currently verifiable from local outputs.",
        },
        "support_level_definitions": {
            "REPRODUCIBLE": "Computed from an existing local output JSON.",
            "DOCUMENT_ONLY": "Found in documents but no local evidence JSON was available.",
            "NEEDS_DATA": "Requires public/raw data or a missing generated output before verification.",
        },
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(_render_markdown(report), encoding="utf-8")
    print(f"Wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def _build_specs(tolerance_override: Optional[float]) -> List[ResultSpec]:
    tol4 = 1e-4 if tolerance_override is None else tolerance_override
    tol3 = 1e-3 if tolerance_override is None else tolerance_override
    specs: List[ResultSpec] = []

    specs.extend(
        [
            ResultSpec(
                result_name="validation_scenario_count",
                thesis_value=8.0,
                evidence_file=DATA / "validation_summary.json",
                compute=lambda: float(len(_read_json(DATA / "validation_summary.json").get("scenarios", []))),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["8 組標準情境", "eight canonical scenarios"],
                suggested_script="python3 scripts/run_demo.py",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="window_matrix_case_count",
                thesis_value=48.0,
                evidence_file=DATA / "window_matrix_summary.json",
                compute=lambda: _json_metric(DATA / "window_matrix_summary.json", ["count"]),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["48 組窗戶矩陣", "48-case window simulation matrix"],
                suggested_script="python3 scripts/run_window_matrix.py",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="window_matrix_target_zone_temperature_in_domain_count",
                thesis_value=34.0,
                evidence_file=DATA / "window_matrix_summary.json",
                compute=lambda: _window_temperature_domain_count(True),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["34 組 target-zone 室內溫度", "34 target-zone temperature cases"],
                suggested_script="python3 scripts/run_window_matrix.py",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="window_matrix_target_zone_temperature_out_of_domain_count",
                thesis_value=14.0,
                evidence_file=DATA / "window_matrix_summary.json",
                compute=lambda: _window_temperature_domain_count(False),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["其餘 14 組保留為範圍外壓力測試", "14 out-of-domain stress cases"],
                suggested_script="python3 scripts/run_window_matrix.py",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="hybrid_default_train_samples",
                thesis_value=576.0,
                evidence_file=DATA / "hybrid_residual_summary.json",
                compute=lambda: _json_metric(DATA / "hybrid_residual_summary.json", ["dataset", "train_samples"]),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["576 個訓練樣本", "576 training"],
                suggested_script="python3 scripts/run_hybrid_residual_experiment.py --fourier-denoise",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="hybrid_default_test_samples",
                thesis_value=192.0,
                evidence_file=DATA / "hybrid_residual_summary.json",
                compute=lambda: _json_metric(DATA / "hybrid_residual_summary.json", ["dataset", "test_samples"]),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["192 個測試樣本", "192 test"],
                suggested_script="python3 scripts/run_hybrid_residual_experiment.py --fourier-denoise",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="hybrid_loo_fold_count",
                thesis_value=8.0,
                evidence_file=DATA / "submission_readiness_summary.json",
                compute=lambda: _json_metric(DATA / "submission_readiness_summary.json", ["leave_one_scenario_out", "fold_count"]),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["8-fold", "leave-one-scenario-out"],
                suggested_script="python3 scripts/run_submission_readiness_experiments.py",
                category="controlled_simulation",
            ),
            ResultSpec(
                result_name="real_bedroom_snapshot_count",
                thesis_value=28.0,
                evidence_file=DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json",
                compute=lambda: _json_metric(DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json", ["snapshot_count"]),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["28 筆快照", "28 cases"],
                suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                category="real_bedroom_snapshot",
            ),
            ResultSpec(
                result_name="e8_completed_real_intervention_trial_count",
                thesis_value=0.0,
                evidence_file=DATA / "e8_intervention_summary.json",
                compute=lambda: _json_metric(
                    DATA / "e8_intervention_summary.json",
                    ["trial_counts", "completed"],
                ),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=[
                    "E8 目前完成真實介入試驗數為 0",
                    "E8 currently has 0 completed real intervention trials",
                ],
                suggested_script="python3 scripts/analyze_e8_intervention_trials.py",
                category="intervention_readiness",
            ),
            ResultSpec(
                result_name="e8_not_evaluated_status_flag",
                thesis_value=1.0,
                evidence_file=DATA / "e8_intervention_summary.json",
                compute=_e8_not_evaluated_status_flag,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["`NOT_EVALUATED`", "\\texttt{NOT\\_EVALUATED}"],
                suggested_script="python3 scripts/analyze_e8_intervention_trials.py",
                category="intervention_readiness",
            ),
            ResultSpec(
                result_name="e8_non_null_efficacy_estimate_count",
                thesis_value=0.0,
                evidence_file=DATA / "e8_intervention_summary.json",
                compute=_e8_non_null_efficacy_count,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=[
                    "所有效益估計維持 null",
                    "all efficacy estimates remain null",
                ],
                suggested_script="python3 scripts/analyze_e8_intervention_trials.py",
                category="intervention_readiness",
            ),
        ]
    )

    for metric, value in {
        "temperature": 0.0474,
        "humidity": 0.1765,
        "illuminance": 2.0269,
    }.items():
        specs.append(
            ResultSpec(
                result_name=f"base_model_average_field_mae.{metric}",
                thesis_value=value,
                evidence_file=DATA / "validation_summary.json",
                compute=lambda metric=metric: _average_scenario_metric(DATA / "validation_summary.json", "field_mae", metric),
                tolerance=tol4,
                thesis_patterns=[f"{value:.4f}"],
                suggested_script="python3 scripts/run_demo.py",
                category="controlled_simulation",
            )
        )

    for metric, value in {
        "temperature": 0.1723,
        "humidity": 0.4633,
        "illuminance": 54.9052,
    }.items():
        specs.append(
            ResultSpec(
                result_name=f"idw_baseline_average_field_mae.{metric}",
                thesis_value=value,
                evidence_file=DATA / "validation_summary.json",
                compute=lambda metric=metric: _average_scenario_metric(DATA / "validation_summary.json", "idw_field_mae", metric),
                tolerance=tol4,
                thesis_patterns=[f"{value:.4f}"],
                suggested_script="python3 scripts/run_demo.py",
                category="controlled_simulation",
            )
        )

    for metric, value in {
        "temperature": 0.0020,
        "humidity": 0.0051,
        "illuminance": 0.1370,
    }.items():
        specs.append(
            ResultSpec(
                result_name=f"hybrid_residual_default_split_field_mae.{metric}",
                thesis_value=value,
                evidence_file=DATA / "hybrid_residual_summary.json",
                compute=lambda metric=metric: _json_metric(DATA / "hybrid_residual_summary.json", ["hybrid_test_field_mae", metric]),
                tolerance=tol4,
                thesis_patterns=[f"{value:.4f}"],
                suggested_script="python3 scripts/run_hybrid_residual_experiment.py --fourier-denoise",
                category="controlled_simulation",
            )
        )

    for metric, value in {
        "temperature": 0.0017,
        "humidity": 0.0059,
        "illuminance": 0.1407,
    }.items():
        specs.append(
            ResultSpec(
                result_name=f"hybrid_residual_loo_average_field_mae.{metric}",
                thesis_value=value,
                evidence_file=DATA / "submission_readiness_summary.json",
                compute=lambda metric=metric: _json_metric(
                    DATA / "submission_readiness_summary.json",
                    ["leave_one_scenario_out", "average_hybrid_field_mae", metric],
                ),
                tolerance=tol4,
                thesis_patterns=[f"{value:.4f}"],
                suggested_script="python3 scripts/run_submission_readiness_experiments.py",
                category="controlled_simulation",
            )
        )

    for prefix, evidence_key, values in [
        (
            "real_bedroom_pillow_mae_before",
            "raw_pillow_mae",
            {"temperature": 0.8967, "humidity": 4.1286, "illuminance": 309.0142},
        ),
        (
            "real_bedroom_pillow_mae_after",
            "estimated_pillow_mae",
            {"temperature": 0.1676, "humidity": 0.3939, "illuminance": 16.6450},
        ),
    ]:
        for metric, value in values.items():
            specs.append(
                ResultSpec(
                    result_name=f"{prefix}.{metric}",
                    thesis_value=value,
                    evidence_file=DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json",
                    compute=lambda metric=metric, evidence_key=evidence_key: _json_metric(
                        DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json",
                        ["aggregate", evidence_key, metric],
                    ),
                    tolerance=tol4 if metric != "illuminance" else tol3,
                    thesis_patterns=[f"{value:.4f}"],
                    suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                    category="real_bedroom_snapshot",
                )
            )

    bootstrap_path = DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json"
    specs.extend(
        [
            ResultSpec(
                result_name="real_bedroom_bootstrap_replicates",
                thesis_value=20000.0,
                evidence_file=bootstrap_path,
                compute=lambda: _json_metric(
                    bootstrap_path,
                    ["aggregate", "paired_day_block_bootstrap", "replicates"],
                ),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["20,000 次"],
                suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                category="real_bedroom_snapshot",
            ),
            ResultSpec(
                result_name="real_bedroom_temperature_improved_snapshots",
                thesis_value=26.0,
                evidence_file=bootstrap_path,
                compute=lambda: _json_metric(
                    bootstrap_path,
                    [
                        "aggregate",
                        "paired_day_block_bootstrap",
                        "metrics",
                        "temperature",
                        "snapshots_improved",
                    ],
                ),
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=["26/28"],
                suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                category="real_bedroom_snapshot",
            ),
        ]
    )
    for metric, reduction, lower, upper in [
        ("temperature", 0.7291, 0.4582, 1.0232),
        ("humidity", 3.7346, 3.2005, 4.2524),
        ("illuminance", 292.3692, 288.3083, 297.0237),
    ]:
        for label, value, path_key in [
            ("mae_reduction", reduction, "absolute_mae_reduction"),
            ("ci95_lower", lower, "lower"),
            ("ci95_upper", upper, "upper"),
        ]:
            metric_path = [
                "aggregate",
                "paired_day_block_bootstrap",
                "metrics",
                metric,
            ]
            if label.startswith("ci95"):
                metric_path.extend(["ci95_absolute_mae_reduction", path_key])
            else:
                metric_path.append(path_key)
            specs.append(
                ResultSpec(
                    result_name=f"real_bedroom_bootstrap_{label}.{metric}",
                    thesis_value=value,
                    evidence_file=bootstrap_path,
                    compute=lambda metric_path=metric_path: _json_metric(bootstrap_path, metric_path),
                    tolerance=tol4,
                    thesis_patterns=[f"{value:.4f}"],
                    suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                    category="real_bedroom_snapshot",
                )
            )

    lodo_path = DATA / "bedroom_01_weekly" / "weekly_simulation_summary.json"
    specs.append(
        ResultSpec(
            result_name="real_bedroom_leave_one_date_out_fold_count",
            thesis_value=7.0,
            evidence_file=lodo_path,
            compute=lambda: _json_metric(
                lodo_path,
                ["aggregate", "leave_one_date_out_sensitivity", "fold_count"],
            ),
            tolerance=0.0 if tolerance_override is None else tolerance_override,
            thesis_patterns=["7-fold leave-one-date-out", "seven-fold leave-one-date-out"],
            suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
            category="real_bedroom_snapshot",
        )
    )
    for metric, value in {
        "temperature": 0.6123,
        "humidity": 3.5551,
        "illuminance": 290.5716,
    }.items():
        specs.append(
            ResultSpec(
                result_name=f"real_bedroom_leave_one_date_out_minimum_reduction.{metric}",
                thesis_value=value,
                evidence_file=lodo_path,
                compute=lambda metric=metric: _json_metric(
                    lodo_path,
                    [
                        "aggregate",
                        "leave_one_date_out_sensitivity",
                        "metrics",
                        metric,
                        "minimum_absolute_mae_reduction",
                    ],
                ),
                tolerance=tol4,
                thesis_patterns=[f"{value:.4f}"],
                suggested_script="python3 scripts/run_bedroom_weekly_simulation.py",
                category="real_bedroom_snapshot",
            )
        )

    public_specs = [
        ("sml2010_public_task_count", 24, DATA / "public_benchmarks" / "sml2010_hybrid_twin_comparison.json", lambda: _public_stats("sml2010")["target_count"], ["SML2010 共 24", "24 個 target-horizon"]),
        ("sml2010_lowest_mae_count", 12, DATA / "public_benchmarks" / "sml2010_hybrid_twin_comparison.json", lambda: _public_stats("sml2010")["lowest_mae_count"], ["12 項取得最低 MAE"]),
        ("sml2010_better_than_linear_regression_count", 15, DATA / "public_benchmarks" / "sml2010_hybrid_twin_comparison.json", lambda: _public_stats("sml2010")["better_than_linear_regression_count"], ["15 項勝過 linear regression"]),
        ("sml2010_better_than_persistence_count", 14, DATA / "public_benchmarks" / "sml2010_hybrid_twin_comparison.json", lambda: _public_stats("sml2010")["better_than_persistence_count"], ["14 項勝過 persistence"]),
        ("cu_bems_public_task_count", 12, DATA / "public_benchmarks" / "cu_bems_hybrid_twin_comparison.json", lambda: _public_stats("cu_bems")["target_count"], ["CU-BEMS 共 12", "12 個 target-horizon"]),
        ("cu_bems_better_than_linear_regression_count", 9, DATA / "public_benchmarks" / "cu_bems_hybrid_twin_comparison.json", lambda: _public_stats("cu_bems")["better_than_linear_regression_count"], ["9 項 MAE 勝過 linear regression", "9 項勝過 linear regression"]),
        ("cu_bems_better_than_persistence_count", 0, DATA / "public_benchmarks" / "cu_bems_hybrid_twin_comparison.json", lambda: _public_stats("cu_bems")["better_than_persistence_count"], ["沒有任務勝過 persistence", "沒有任何一項勝過 persistence"]),
    ]
    for result_name, thesis_value, evidence_file, compute, patterns in public_specs:
        dataset = "sml2010" if result_name.startswith("sml2010") else "cu-bems"
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=float(thesis_value),
                evidence_file=evidence_file,
                compute=compute,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=patterns,
                suggested_script=(
                    "python3 scripts/run_public_dataset_benchmark.py --dataset {dataset} --horizons 15,60 && "
                    "python3 scripts/run_public_dataset_model_comparison.py --dataset {dataset} --horizons 15,60"
                ).format(dataset=dataset),
                category="public_task_aligned_benchmark",
                needs_public_data=True,
            )
        )

    oh2024_path = DATA / "public_benchmarks" / "oh2024_inspired_sml2010_comparison.json"
    oh2024_specs = [
        (
            "oh2024_transfer_evaluated_case_count",
            6.0,
            lambda: _json_metric(oh2024_path, ["summary", "evaluated_cases"]),
            ["6 個 temperature target--horizon", "6 個 SML2010 temperature target-horizon"],
        ),
        (
            "oh2024_transfer_wins_vs_raw_physics",
            4.0,
            lambda: _json_metric(oh2024_path, ["summary", "oh2024_inspired_wins_vs_raw_physics"]),
            ["實際結果為 4/6", "4/6"],
        ),
        (
            "oh2024_transfer_15min_dining_mae",
            0.042169,
            lambda: _oh2024_case_metric("dining_temperature", 15, "oh2024_inspired_additive_residual", "mae"),
            ["0.0422"],
        ),
        (
            "oh2024_transfer_15min_room_mae",
            0.051743,
            lambda: _oh2024_case_metric("room_temperature", 15, "oh2024_inspired_additive_residual", "mae"),
            ["0.0517"],
        ),
        (
            "oh2024_transfer_1440min_dining_mae",
            1.753754,
            lambda: _oh2024_case_metric("dining_temperature", 1440, "oh2024_inspired_additive_residual", "mae"),
            ["1.7538"],
        ),
        (
            "oh2024_transfer_1440min_room_mae",
            1.772293,
            lambda: _oh2024_case_metric("room_temperature", 1440, "oh2024_inspired_additive_residual", "mae"),
            ["1.7723"],
        ),
    ]
    for result_name, thesis_value, compute, patterns in oh2024_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=oh2024_path,
                compute=compute,
                tolerance=tol4,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_oh2024_inspired_comparison.py",
                category="public_task_method_transfer",
                needs_public_data=True,
            )
        )

    next_day_path = DATA / "public_benchmarks" / "next_day_temperature_improvement.json"
    next_day_specs = [
        ("next_day_persistence_dining_mae", 1.517486, lambda: _next_day_primary_metric("dining_temperature", "seasonal_persistence", "mae"), ["1.5175"]),
        ("next_day_persistence_room_mae", 1.499639, lambda: _next_day_primary_metric("room_temperature", "seasonal_persistence", "mae"), ["1.4996"]),
        ("next_day_selected_dining_mae", 1.628868, lambda: _next_day_selected_metric("dining_temperature", "mae"), ["1.6289"]),
        ("next_day_selected_room_mae", 1.624972, lambda: _next_day_selected_metric("room_temperature", "mae"), ["1.6250"]),
        ("next_day_bias_corrected_dining_mae", 1.501763, lambda: _next_day_primary_metric("dining_temperature", "bias_corrected_persistence", "mae"), ["1.5018"]),
        ("next_day_bias_corrected_room_mae", 1.488394, lambda: _next_day_primary_metric("room_temperature", "bias_corrected_persistence", "mae"), ["1.4884"]),
        ("next_day_adaptive_selected_dining_mae", 1.651511, lambda: _next_day_adaptive_selected_metric("dining_temperature", "mae"), ["1.6515"]),
        ("next_day_adaptive_selected_room_mae", 1.645603, lambda: _next_day_adaptive_selected_metric("room_temperature", "mae"), ["1.6456"]),
    ]
    for result_name, thesis_value, compute, patterns in next_day_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=next_day_path,
                compute=compute,
                tolerance=tol4,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_next_day_temperature_comparison.py",
                category="public_task_next_day_followup",
                needs_public_data=True,
            )
        )

    rnn_3d_path = DATA / "rnn_3d_field_comparison.json"
    rnn_3d_specs = [
        (
            "rnn_3d_complete_status",
            1.0,
            _rnn_3d_complete_status_flag,
            ["資料 parity 8/8 通過", "Across eight leave-one-scenario-out folds"],
        ),
        (
            "rnn_3d_parity_passed",
            1.0,
            _rnn_3d_data_parity_flag,
            ["資料 parity 8/8 通過", "eight leave-one-scenario-out folds"],
        ),
        (
            "rnn_3d_temperature_mae",
            0.209125,
            lambda: _json_metric(rnn_3d_path, ["summary", "average_field_mae", "pure_rnn", "temperature"]),
            ["0.2091"],
        ),
        (
            "rnn_3d_humidity_mae",
            0.224112,
            lambda: _json_metric(rnn_3d_path, ["summary", "average_field_mae", "pure_rnn", "humidity"]),
            ["0.2241"],
        ),
        (
            "rnn_3d_illuminance_mae",
            48.142175,
            lambda: _json_metric(rnn_3d_path, ["summary", "average_field_mae", "pure_rnn", "illuminance"]),
            ["48.1422"],
        ),
        (
            "rnn_3d_lowest_mae_count",
            0.0,
            lambda: _json_metric(rnn_3d_path, ["summary", "lowest_mae_counts_over_24_fold_metrics", "pure_rnn"]),
            ["0/24", "0 of 24 fold-factor comparisons"],
        ),
    ]
    for result_name, thesis_value, compute, patterns in rnn_3d_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=rnn_3d_path,
                compute=compute,
                tolerance=tol4,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_rnn_3d_field_comparison.py",
                category="controlled_synthetic_rnn_3d_field_comparison",
            )
        )

    rnn_path = DATA / "public_benchmarks" / "rnn_sml2010_comparison.json"
    rnn_specs = [
        (
            "rnn_same_data_complete_status",
            1.0,
            _rnn_complete_status_flag,
            ["RNN 同資料比較為 `COMPLETE`", "RNN same-data comparison is complete"],
        ),
        (
            "rnn_same_data_parity_passed",
            1.0,
            _rnn_data_parity_flag,
            ["12/12 個案例通過資料一致性", "all 12 cases passed the data-parity audit"],
        ),
        (
            "rnn_same_data_evaluated_case_count",
            12.0,
            lambda: _json_metric(rnn_path, ["summary", "evaluated_cases"]),
            ["12 個 target--horizon 案例", "12 target--horizon cases"],
        ),
        (
            "rnn_lowest_mae_count",
            0.0,
            lambda: _json_metric(rnn_path, ["summary", "lowest_mae_counts", "vanilla_rnn"]),
            ["RNN 為 0 項", "RNN was lowest in 0"],
        ),
        (
            "rnn_sequence_linear_lowest_mae_count",
            7.0,
            lambda: _json_metric(rnn_path, ["summary", "lowest_mae_counts", "sequence_linear_regression"]),
            ["sequence linear regression 為 7 項", "sequence linear regression in 7"],
        ),
        (
            "rnn_persistence_lowest_mae_count",
            5.0,
            lambda: _json_metric(rnn_path, ["summary", "lowest_mae_counts", "persistence"]),
            ["persistence 為 5 項", "persistence in 5"],
        ),
    ]
    for result_name, thesis_value, compute, patterns in rnn_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=rnn_path,
                compute=compute,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_rnn_public_comparison.py",
                category="public_task_rnn_same_data_comparison",
                needs_public_data=True,
            )
        )

    kalman_path = DATA / "public_benchmarks" / "kalman_sml2010_filtering_comparison.json"
    kalman_specs = [
        (
            "kalman_controlled_filtering_complete_status",
            1.0,
            _kalman_complete_status_flag,
            ["Kalman 受控同資料比較為 `COMPLETE`", "Kalman controlled same-data comparison is complete"],
        ),
        (
            "kalman_controlled_filtering_parity_passed",
            1.0,
            _kalman_data_parity_flag,
            ["12/12 Kalman 案例通過資料一致性", "all 12 Kalman cases passed data parity"],
        ),
        (
            "kalman_controlled_filtering_case_count",
            12.0,
            lambda: _json_metric(kalman_path, ["summary", "evaluated_cases"]),
            ["12 個受控 filtering 案例", "12 controlled filtering cases"],
        ),
        (
            "kalman_lowest_mae_count",
            6.0,
            lambda: _json_metric(kalman_path, ["summary", "lowest_mae_counts", "linear_kalman_random_walk"]),
            ["Linear Kalman 為 6 項", "linear Kalman was lowest in 6"],
        ),
        (
            "kalman_moving_average_lowest_mae_count",
            6.0,
            lambda: _json_metric(kalman_path, ["summary", "lowest_mae_counts", "causal_moving_average_3"]),
            ["MA(3) 為 6 項", "moving average was lowest in 6"],
        ),
        (
            "kalman_raw_lowest_mae_count",
            0.0,
            lambda: _json_metric(kalman_path, ["summary", "lowest_mae_counts", "raw_noisy"]),
            ["未濾波為 0 項", "raw observation was lowest in 0"],
        ),
        (
            "kalman_wins_vs_raw_count",
            12.0,
            lambda: _json_metric(kalman_path, ["summary", "kalman_wins_vs", "raw_noisy"]),
            ["Kalman 在 12 項都優於未濾波", "Kalman beat the raw observation in all 12"],
        ),
    ]
    for result_name, thesis_value, compute, patterns in kalman_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=kalman_path,
                compute=compute,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_kalman_filter_comparison.py",
                category="public_task_controlled_kalman_filtering",
                needs_public_data=True,
            )
        )

    enclosure_path = DATA / "enclosure" / "enclosure_bmc_baseline.json"
    enclosure_specs = [
        (
            "enclosure_bmc_source_file_count",
            124.0,
            lambda: float(len({case["source_file"] for case in _read_json(enclosure_path)["cases"]})),
            ["124 個 source CSV", "124 public BMC CSV files"],
        ),
        (
            "enclosure_bmc_file_device_case_count",
            317.0,
            lambda: _json_metric(enclosure_path, ["summary", "case_count"]),
            ["317 個 file-device cases", "317 file-device cases"],
        ),
        (
            "enclosure_bmc_evaluated_case_count",
            5.0,
            lambda: _json_metric(enclosure_path, ["summary", "evaluated_case_count"]),
            ["5 個案例可評估", "Only 5 cases met"],
        ),
        (
            "enclosure_thermal_balance_wins_vs_persistence",
            0.0,
            lambda: _json_metric(enclosure_path, ["summary", "thermal_balance_wins_vs_persistence"]),
            ["thermal-balance 對 persistence 為 0/5", "thermal-balance readout won 0"],
        ),
        (
            "enclosure_persistence_lowest_mae_count",
            5.0,
            lambda: _json_metric(enclosure_path, ["summary", "lowest_test_mae_counts", "persistence"]),
            ["Persistence 在 5/5 案例取得最低", "persistence was lowest-MAE in all 5"],
        ),
    ]
    for result_name, thesis_value, compute, patterns in enclosure_specs:
        specs.append(
            ResultSpec(
                result_name=result_name,
                thesis_value=thesis_value,
                evidence_file=enclosure_path,
                compute=compute,
                tolerance=0.0 if tolerance_override is None else tolerance_override,
                thesis_patterns=patterns,
                suggested_script="python3 scripts/run_enclosure_bmc_baseline.py /path/to/bmcdata/data/*.csv",
                category="public_task_equipment_enclosure_transfer",
                needs_public_data=True,
            )
        )
    return specs


def _evaluate_spec(spec: ResultSpec) -> Dict[str, object]:
    thesis_sources = _find_thesis_sources(spec.thesis_patterns)
    missing_reasons = []
    computed_value: Optional[float] = None
    absolute_error: Optional[float] = None

    if not thesis_sources:
        missing_reasons.append(f"Thesis value/pattern not found: {list(spec.thesis_patterns)}")

    if not spec.evidence_file.exists():
        missing_reasons.append(f"Missing evidence file: {spec.evidence_file.relative_to(ROOT)}")
        return _result_payload(
            spec=spec,
            thesis_sources=thesis_sources,
            computed_value=None,
            absolute_error=None,
            status="MISSING",
            support_level="NEEDS_DATA" if spec.needs_public_data else "DOCUMENT_ONLY",
            missing_reasons=missing_reasons,
        )

    try:
        computed_value = float(spec.compute())
    except Exception as exc:  # noqa: BLE001 - report verification errors without hiding other rows.
        missing_reasons.append(f"Could not compute value from evidence: {exc}")
        return _result_payload(
            spec=spec,
            thesis_sources=thesis_sources,
            computed_value=None,
            absolute_error=None,
            status="MISSING",
            support_level="NEEDS_DATA" if spec.needs_public_data else "DOCUMENT_ONLY",
            missing_reasons=missing_reasons,
        )

    absolute_error = abs(float(spec.thesis_value) - computed_value)
    if missing_reasons:
        status = "MISSING"
    elif absolute_error <= spec.tolerance:
        status = "PASS"
    else:
        status = "FAIL"
    return _result_payload(
        spec=spec,
        thesis_sources=thesis_sources,
        computed_value=computed_value,
        absolute_error=absolute_error,
        status=status,
        support_level="REPRODUCIBLE",
        missing_reasons=missing_reasons,
    )


def _result_payload(
    spec: ResultSpec,
    thesis_sources: List[str],
    computed_value: Optional[float],
    absolute_error: Optional[float],
    status: str,
    support_level: str,
    missing_reasons: List[str],
) -> Dict[str, object]:
    return {
        "result_name": spec.result_name,
        "category": spec.category,
        "thesis_value": spec.thesis_value,
        "computed_value": computed_value,
        "absolute_error": absolute_error,
        "tolerance": spec.tolerance,
        "status": status,
        "support_level": support_level,
        "source_file": thesis_sources,
        "evidence_file": str(spec.evidence_file.relative_to(ROOT)),
        "suggested_script": spec.suggested_script,
        "missing_reason": missing_reasons,
    }


def _find_thesis_sources(patterns: Sequence[str]) -> List[str]:
    sources = []
    for path in THESIS_SOURCES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern in text for pattern in patterns):
            sources.append(str(path.relative_to(ROOT)))
    return sources


def _average_scenario_metric(path: Path, key: str, metric: str) -> float:
    payload = _read_json(path)
    scenarios = payload.get("scenarios", [])
    if not scenarios:
        raise ValueError("validation_summary.json has no scenarios")
    return sum(float(item[key][metric]) for item in scenarios) / float(len(scenarios))


def _json_metric(path: Path, keys: Sequence[str]) -> float:
    payload = _read_json(path)
    node = payload
    for key in keys:
        node = node[key]
    return float(node)


def _window_temperature_domain_count(in_domain: bool) -> float:
    payload = _read_json(DATA / "window_matrix_summary.json")
    temperatures = [
        float(item["target_zone_estimated"]["temperature"])
        for item in payload.get("scenarios", [])
    ]
    count = sum(20.0 <= value <= 30.0 for value in temperatures)
    return float(count if in_domain else len(temperatures) - count)


def _public_stats(dataset_key: str) -> Dict[str, int]:
    path = DATA / "public_benchmarks" / f"{dataset_key}_hybrid_twin_comparison.json"
    payload = _read_json(path)
    model_name = payload.get("mapped_model_name", "hybrid_digital_twin_readout")
    target_count = 0
    lowest_mae_count = 0
    better_than_linear_regression_count = 0
    better_than_persistence_count = 0
    for task in payload.get("tasks", []):
        if task.get("status") != "ok":
            continue
        for target in task.get("targets", {}).values():
            target_count += 1
            model_mae = float(target[model_name]["mae"])
            persistence_mae = float(target["persistence"]["mae"])
            linear_mae = float(target["linear_regression"]["mae"])
            if model_mae < linear_mae:
                better_than_linear_regression_count += 1
            if model_mae < persistence_mae:
                better_than_persistence_count += 1
            if model_mae < min(persistence_mae, linear_mae):
                lowest_mae_count += 1
    return {
        "target_count": target_count,
        "lowest_mae_count": lowest_mae_count,
        "better_than_linear_regression_count": better_than_linear_regression_count,
        "better_than_persistence_count": better_than_persistence_count,
    }


def _oh2024_case_metric(target: str, horizon_minutes: int, method: str, metric: str) -> float:
    path = DATA / "public_benchmarks" / "oh2024_inspired_sml2010_comparison.json"
    payload = _read_json(path)
    for case in payload.get("cases", []):
        if (
            case.get("status") == "ok"
            and case.get("target") == target
            and int(case.get("horizon_minutes", 0)) == horizon_minutes
        ):
            return float(case["metrics"][method][metric])
    raise ValueError(f"Missing Oh2024 transfer case: {target}, {horizon_minutes}")


def _next_day_case(target: str) -> Dict[str, object]:
    path = DATA / "public_benchmarks" / "next_day_temperature_improvement.json"
    payload = _read_json(path)
    for case in payload.get("cases", []):
        if case.get("status") == "ok" and case.get("target") == target:
            return case
    raise ValueError(f"Missing next-day primary case: {target}")


def _next_day_primary_metric(target: str, candidate: str, metric: str) -> float:
    case = _next_day_case(target)
    return float(case["final_test_candidate_metrics"][candidate]["test_metrics"][metric])


def _next_day_selected_metric(target: str, metric: str) -> float:
    case = _next_day_case(target)
    selected = str(case["selected_candidate"])
    return float(case["final_test_candidate_metrics"][selected]["test_metrics"][metric])


def _next_day_adaptive_selected_metric(target: str, metric: str) -> float:
    path = DATA / "public_benchmarks" / "next_day_temperature_improvement.json"
    payload = _read_json(path)
    for case in payload.get("adaptive_online_followup", {}).get("cases", []):
        if case.get("target") == target:
            selected = str(case["selected_candidate"])
            return float(case["test_metrics"][selected][metric])
    raise ValueError(f"Missing next-day adaptive case: {target}")


def _e8_not_evaluated_status_flag() -> float:
    payload = _read_json(DATA / "e8_intervention_summary.json")
    return 1.0 if payload.get("evidence_status") == "NOT_EVALUATED" else 0.0


def _e8_non_null_efficacy_count() -> float:
    payload = _read_json(DATA / "e8_intervention_summary.json")
    metrics = payload.get("metrics", {})
    selected = [
        metrics.get("top_ranked_success_rate"),
        metrics.get("top_ranked_mean_actual_improvement"),
        metrics.get("mean_absolute_prediction_error"),
        metrics.get("overall_direction_accuracy"),
        metrics.get("matched_block_top1_regret_mean"),
        metrics.get("matched_block_spearman_mean"),
    ]
    selected.extend(metrics.get("direction_accuracy", {}).values())
    return float(sum(value is not None for value in selected))


def _rnn_complete_status_flag() -> float:
    payload = _read_json(DATA / "public_benchmarks" / "rnn_sml2010_comparison.json")
    return 1.0 if payload.get("status") == "COMPLETE" else 0.0


def _rnn_3d_complete_status_flag() -> float:
    payload = _read_json(DATA / "rnn_3d_field_comparison.json")
    return 1.0 if payload.get("status") == "COMPLETE" else 0.0


def _rnn_3d_data_parity_flag() -> float:
    payload = _read_json(DATA / "rnn_3d_field_comparison.json")
    folds = payload.get("folds", [])
    return 1.0 if (
        payload.get("data_parity", {}).get("all_folds_passed") is True
        and len(folds) == 8
        and all(fold.get("data_parity", {}).get("passed") is True for fold in folds)
    ) else 0.0


def _rnn_data_parity_flag() -> float:
    payload = _read_json(DATA / "public_benchmarks" / "rnn_sml2010_comparison.json")
    audits = payload.get("data_parity", {}).get("horizon_audits", [])
    method_hashes_match = bool(audits) and all(
        len(
            {
                contract.get("shared_test_input_hash")
                for contract in audit.get("method_data_contracts", {}).values()
            }
        )
        == 1
        for audit in audits
    )
    return 1.0 if payload.get("data_parity", {}).get("all_horizons_passed") and method_hashes_match else 0.0


def _kalman_complete_status_flag() -> float:
    payload = _read_json(DATA / "public_benchmarks" / "kalman_sml2010_filtering_comparison.json")
    return 1.0 if payload.get("status") == "COMPLETE" else 0.0


def _kalman_data_parity_flag() -> float:
    payload = _read_json(DATA / "public_benchmarks" / "kalman_sml2010_filtering_comparison.json")
    return 1.0 if payload.get("summary", {}).get("all_cases_data_parity_passed") is True else 0.0


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _summarize(results: Sequence[Dict[str, object]]) -> Dict[str, int]:
    output = {"PASS": 0, "FAIL": 0, "MISSING": 0, "TOTAL": len(results)}
    for result in results:
        output[result["status"]] += 1
    return output


def _render_markdown(report: Dict[str, object]) -> str:
    lines = [
        "# Thesis Result Verification Report",
        "",
        "This report compares hard-coded thesis/paper values against local `outputs/data` evidence JSON files.",
        "",
        "## Summary",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Results",
            "",
            "| result_name | thesis_value | computed_value | abs_error | tolerance | status | support | evidence |",
            "|---|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for result in report["results"]:
        lines.append(
            "| {result_name} | {thesis_value} | {computed_value} | {absolute_error} | {tolerance} | {status} | {support_level} | `{evidence_file}` |".format(
                result_name=result["result_name"],
                thesis_value=_fmt(result["thesis_value"]),
                computed_value=_fmt(result["computed_value"]),
                absolute_error=_fmt(result["absolute_error"]),
                tolerance=_fmt(result["tolerance"]),
                status=result["status"],
                support_level=result["support_level"],
                evidence_file=result["evidence_file"],
            )
        )
    lines.extend(["", "## Missing Or Failed Details", ""])
    any_detail = False
    for result in report["results"]:
        if result["status"] == "PASS":
            continue
        any_detail = True
        lines.append(f"### {result['result_name']}")
        for reason in result["missing_reason"]:
            lines.append(f"- {reason}")
        lines.append(f"- suggested_script: `{result['suggested_script']}`")
        lines.append("")
    if not any_detail:
        lines.append("No missing or failed result rows.")
    return "\n".join(lines).strip() + "\n"


def _fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


if __name__ == "__main__":
    main()
