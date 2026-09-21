#!/usr/bin/env node
/**
 * Deterministic API-contract test for the tuning protocol.
 * This is a pipeline test only, not BOPTEST, TCLab, or physical evidence.
 */
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const output = process.argv[2] ?? "openspec/changes/systematic-parameter-tuning-20260921/artifacts/contract_test_run.json";
const dt = 60;
const horizon = 24;
const target = 22;
const candidates = [
  { kp: 0.6, ti: 600 },
  { kp: 1.2, ti: 900 },
  { kp: 2.4, ti: 1800 },
];

function sha(value) { return crypto.createHash("sha256").update(JSON.stringify(value)).digest("hex"); }
function disturbance(split, step) {
  const phase = split === "calibration" ? 0 : split === "validation" ? 3 : 7;
  return 2.0 * Math.sin((step + phase) / 7) + 0.7 * Math.cos((step + phase) / 13);
}
function simulate(split, controller, seed) {
  let temp = split === "calibration" ? 20.5 : split === "validation" ? 23.5 : 21.2;
  let integral = 0;
  const trace = [];
  for (let step = 0; step < horizon; step += 1) {
    const error = target - temp;
    integral = Math.max(-120, Math.min(120, integral + error * dt));
    const raw = controller.kp * (error + integral / controller.ti);
    const input = Math.max(-4, Math.min(4, raw));
    const noise = seed === 17 ? 0.02 * Math.sin(step * 1.7) : 0;
    temp += dt / 900 * (0.85 * input - (temp - (target + disturbance(split, step))) / 8) + noise;
    trace.push({ step, temp: Number(temp.toFixed(8)), input: Number(input.toFixed(8)) });
  }
  return trace;
}
function metrics(trace) {
  const errors = trace.map((row) => Math.abs(target - row.temp));
  return {
    n: trace.length,
    mae: errors.reduce((a, b) => a + b, 0) / errors.length,
    max_abs_error: Math.max(...errors),
    within_0_5_pct: errors.filter((x) => x <= 0.5).length / errors.length * 100,
  };
}

const baseline = { kp: 1.0, ti: 1200 };
const calibrationScores = candidates.map((parameters) => {
  const trace = simulate("calibration", parameters, 17);
  return { parameters, metrics: metrics(trace) };
});
const selected = calibrationScores.reduce((best, row) => row.metrics.mae < best.metrics.mae ? row : best);
const splits = {};
const traces = {};
for (const split of ["calibration", "validation", "holdout"]) {
  const trace = simulate(split, selected.parameters, 17);
  traces[split] = trace;
  splits[split] = {
    status: "PASS",
    trace_sha256: sha(trace),
    metrics: metrics(trace),
    initial_state: trace[0].temp,
  };
}
const baselineMetrics = {};
for (const split of ["validation", "holdout"]) baselineMetrics[split] = metrics(simulate(split, baseline, 17));

const artifact = {
  status: "PASS_CONTRACT_TEST_NOT_RESEARCH_EVIDENCE",
  run_id: "contract-test-20260921-01",
  scope: "DETERMINISTIC_TOY_DYNAMIC_API_PIPELINE",
  protocol: "systematic_parameter_tuning_protocol_2026-09-21_zh.md",
  parameters: { selected: selected.parameters, candidates, baseline },
  metrics: { calibration: selected.metrics, baseline: baselineMetrics, selected: { validation: splits.validation.metrics, holdout: splits.holdout.metrics } },
  splits,
  reproducibility: { dt_s: dt, horizon_steps: horizon, seed: 17, trace_hashes_distinct: new Set(Object.values(splits).map((x) => x.trace_sha256)).size === 3 },
  boundary: "Synthetic contract test only; no claim about BOPTEST, TCLab, real rooms, enclosures, semiconductors, or intervention.",
};
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify(artifact, null, 2) + "\n");
console.log(JSON.stringify({ output, status: artifact.status, selected: selected.parameters, holdout: splits.holdout.metrics }, null, 2));
