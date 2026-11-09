#!/usr/bin/env python3
"""Check manuscript numbers against the frozen result and export 60 episode rows."""
from pathlib import Path
import csv
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "openspec/changes/compare-enclosure-five-methods-20261026/artifacts"
data = (ART / "result.json").read_bytes()
result = json.loads(data)
verification = json.loads((ART / "verification.json").read_text())
assert verification["status"] == "PASS"
assert hashlib.sha256(data).hexdigest() == verification["result_sha256"]
assert verification["evaluation_episodes"] == 60
assert verification["calibration_episodes"] == 45
assert verification["rows"] == 12600
assert len(result["runs"]) == 60

split_map = {"驗證": "validation", "保留": "holdout", "失配": "plant_holdout", "過載": "overload"}
method_map = {"固定PWM": "fixed", "PI": "pi", "PID": "pid", "LQR": "lqr", "MPC": "mpc"}
source = (HERE / "manuscript_zh.md").read_text()
table = source.split("**表三", 1)[1].split("在保留測試組", 1)[0]
rows = []
for line in table.splitlines():
    if line.startswith("| "):
        vals = [v.strip() for v in line.strip().strip("|").split("|")]
        if len(vals) == 5 and vals[0] in split_map:
            rows.append(vals)
assert len(rows) == 20, len(rows)
for name, method, mae, energy, overtemp in rows:
    actual = result["aggregates"][split_map[name]][method_map[method]]
    for printed, key in [(mae, "tracking_mae_C"), (energy, "fan_energy_proxy_Wh"), (overtemp, "overtemp_s")]:
        tolerance = 0.051 if key == "overtemp_s" else 0.000051
        assert abs(float(printed) - actual[key]) <= tolerance, (name, method, key)

table4 = source.split("**表四", 1)[1].split("![圖二", 1)[0]
range_rows = []
for line in table4.splitlines():
    if line.startswith("| "):
        vals = [v.strip() for v in line.strip().strip("|").split("|")]
        if len(vals) == 4 and vals[0] in split_map:
            range_rows.append(vals)
assert len(range_rows) == 4
for name, *ranges in range_rows:
    for method, shown in zip(("pid", "lqr", "mpc"), ranges):
        vals = [r["metrics"]["tracking_mae_C"] for r in result["runs"]
                if r["split"] == split_map[name] and r["method"] == method]
        lower, upper = shown.split("–")
        assert abs(float(lower) - min(vals)) <= 0.000501
        assert abs(float(upper) - max(vals)) <= 0.000501

holdout = result["aggregates"]["holdout"]
pid, lqr = holdout["pid"], holdout["lqr"]
mae_delta = 100 * (pid["tracking_mae_C"] - lqr["tracking_mae_C"]) / pid["tracking_mae_C"]
energy_delta = 100 * (lqr["fan_energy_proxy_Wh"] - pid["fan_energy_proxy_Wh"]) / pid["fan_energy_proxy_Wh"]
assert abs(mae_delta - 38.35) < 0.005
assert abs(energy_delta - 15.83) < 0.005

out = HERE / "supplement_60_runs.csv"
columns = ["split", "seed", "method", "parameters_json", "tracking_mae_C", "fan_energy_proxy_Wh",
           "overtemp_s", "fallback_n", "bounds_violations", "slew_violations", "trace_sha256"]
with out.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, columns)
    writer.writeheader()
    for run in result["runs"]:
        m = run["metrics"]
        writer.writerow({"split": run["split"], "seed": run["seed"], "method": run["method"],
                         "parameters_json": json.dumps(run["parameters"], sort_keys=True),
                         "tracking_mae_C": f'{m["tracking_mae_C"]:.8f}',
                         "fan_energy_proxy_Wh": f'{m["fan_energy_proxy_Wh"]:.8f}',
                         "overtemp_s": f'{m["overtemp_s"]:.4f}',
                         "fallback_n": m["fallback_n"],
                         "bounds_violations": m["bounds_violations"],
                         "slew_violations": m["slew_violations"],
                         "trace_sha256": run["trace_sha256"]})

calibration = json.loads((ART / "calibration.json").read_text())
calibration_rows = [run for candidates in calibration["candidates"].values()
                    for candidate in candidates for run in candidate["runs"]]
assert len(calibration_rows) == 45
assert all(run["n"] == 120 and run["split"] == "calibration" for run in calibration_rows)
candidate_means = {(method, index): candidate["score"]
                   for method, candidates in calibration["candidates"].items()
                   for index, candidate in enumerate(candidates)}
for run in calibration_rows + result["runs"]:
    trace = ART / run["trace_path"]
    assert trace.is_file() and hashlib.sha256(trace.read_bytes()).hexdigest() == run["trace_sha256"]
calibration_columns = ["method", "candidate_index", "seed", "parameters_json", "candidate_mean_selection_score", "selected", "selection_score",
                       "tracking_mae_C", "fan_energy_proxy_Wh", "overtemp_s", "fallback_n", "trace_sha256"]
with (HERE / "supplement_45_calibration_runs.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, calibration_columns)
    writer.writeheader()
    for run in calibration_rows:
        m = run["metrics"]
        writer.writerow({"method": run["method"], "candidate_index": run["candidate_index"],
                         "seed": run["seed"],
                         "parameters_json": json.dumps(run["parameters"], sort_keys=True),
                         "candidate_mean_selection_score": f'{candidate_means[(run["method"], run["candidate_index"])]:.8f}',
                         "selected": int(run["parameters"] == calibration["selected"][run["method"]]),
                         "selection_score": f'{m["selection_score"]:.8f}',
                         "tracking_mae_C": f'{m["tracking_mae_C"]:.8f}',
                         "fan_energy_proxy_Wh": f'{m["fan_energy_proxy_Wh"]:.8f}',
                         "overtemp_s": f'{m["overtemp_s"]:.4f}',
                         "fallback_n": m["fallback_n"],
                         "trace_sha256": run["trace_sha256"]})

evidence = []
for name, method, mae, energy, overtemp in rows:
    for label, value, key, unit in [
        ("MAE", mae, "tracking_mae_C", "°C"),
        ("風扇代價代理", energy, "fan_energy_proxy_Wh", "Wh/回合"),
        ("取樣超溫", overtemp, "overtemp_s", "秒/回合"),
    ]:
        evidence.append({"claim": f"表三 {name} {method} {label}", "value": value,
                         "unit": unit, "source_file": "artifacts/result.json",
                         "source_field": f"aggregates.{split_map[name]}.{method_map[method]}.{key}",
                         "scope": "三正式回合等權平均"})
for name, *ranges in range_rows:
    for method, shown in zip(("pid", "lqr", "mpc"), ranges):
        evidence.append({"claim": f"表四 {name} {method.upper()} MAE範圍", "value": shown,
                         "unit": "°C", "source_file": "artifacts/result.json",
                         "source_field": f"runs[split={split_map[name]},method={method}].metrics.tracking_mae_C",
                         "scope": "三正式回合之最小至最大值；非信賴區間"})
for claim, value, source_file, source_field, scope in [
    ("校準回合", "45", "artifacts/verification.json", "calibration_episodes", "三候選×三種子×五方法"),
    ("正式回合", "60", "artifacts/verification.json", "evaluation_episodes", "四分組×三種子×五方法"),
    ("軌跡列數", "12600", "artifacts/verification.json", "rows", "105回合×120步"),
    ("保留組LQR相對PID MAE降低", f"{mae_delta:.2f}", "artifacts/result.json", "aggregates.holdout.{lqr,pid}.tracking_mae_C", "未四捨五入值計算百分比"),
    ("保留組LQR相對PID代價提高", f"{energy_delta:.2f}", "artifacts/result.json", "aggregates.holdout.{lqr,pid}.fan_energy_proxy_Wh", "未四捨五入值計算百分比"),
    ("執行環境版本", "Python 3.11.15; NumPy 1.26.4; SciPy 1.14.1; OSQP 1.0.4", "artifacts/freeze.json", "environment", "凍結軟體環境"),
    ("失配設定", "三組參數倍率與tau", "config.json", "variants[0:3]", "正文第二節逐seed列示"),
    ("求解器設定", "eps_abs=eps_rel=1e-7; max_iter=100000; residual_tol=1e-5", "artifacts/source_snapshots/digital_twin/control/enclosure_control_v2.py", "OSQP_OPTIONS; RESIDUAL_TOL", "凍結來源碼"),
    ("MPC固定權重與軟性溫度上限", "delta_weight=5; slack_weight=10000; margin_C=2; caps=78/83°C", "config.json", "settings.delta_weight; settings.slack_weight; settings.margin_C; settings.limits_C", "MPC候選僅改input_weight"),
    ("LQR工作點與回授", "equilibrium objective=sum(((T_eq-60)/5)^2)+u^2; ZOH; DARE; Q=diag(.04,.04,0)", "artifacts/source_snapshots/digital_twin/control/enclosure_control_v2.py", "equilibrium_allocation; _lqr", "名義模型與當下入口/功率"),
]:
    evidence.append({"claim": claim, "value": value, "unit": "%" if "相對" in claim else "",
                     "source_file": source_file, "source_field": source_field, "scope": scope})
with (HERE / "claim_evidence.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, ["claim", "value", "unit", "source_file", "source_field", "scope"])
    writer.writeheader()
    writer.writerows(evidence)

print(f"PASS: 20 aggregate rows, 12 ranges, 2 percentages; 45 calibration + 60 evaluation episodes and {len(evidence)} claim rows exported; result SHA256 {verification['result_sha256']}")
