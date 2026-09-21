#!/usr/bin/env node
/** Validate the systematic parameter-tuning evidence gate. */
import fs from "node:fs";

const args = process.argv.slice(2);
const reportOnly = args.includes("--report-only");
const input = args.find((arg) => !arg.startsWith("--")) ??
  "openspec/changes/systematic-parameter-tuning-20260921/artifacts/protocol_audit.json";

const doc = JSON.parse(fs.readFileSync(input, "utf8"));
const reasons = [];

if (doc.checks) {
  if (doc.checks.calibration_search_budget_recorded !== true) reasons.push("calibration search budget is not recorded");
  if (doc.checks.validation_metrics_recorded !== true) reasons.push("validation metrics are not recorded");
  if (doc.checks.trace_hashes_recorded !== true) reasons.push("trace hashes are not recorded");
  if (doc.checks.independent_holdout !== true || doc.holdout?.status !== "PASS") reasons.push("independent sealed holdout is missing");
  if (doc.checks.public_rest_equivalence === true) reasons.push("public REST equivalence needs separate evidence");
} else {
  if (!doc.run_id) reasons.push("run_id is missing");
  if (!doc.parameters || typeof doc.parameters !== "object") reasons.push("parameters JSON is missing");
  if (!doc.metrics || typeof doc.metrics !== "object") reasons.push("metrics JSON is missing");
  const splits = doc.splits ?? {};
  for (const name of ["calibration", "validation", "holdout"]) {
    if (!splits[name]?.trace_sha256) reasons.push(`${name} trace hash is missing`);
  }
  const hashes = ["calibration", "validation", "holdout"].map((name) => splits[name]?.trace_sha256).filter(Boolean);
  if (new Set(hashes).size !== hashes.length) reasons.push("split trace hashes are not independent");
  if (splits.holdout?.status !== "PASS") reasons.push("holdout status is not PASS");
}

const status = reasons.length === 0 ? "PASS" : "PILOT_INCOMPLETE";
console.log(JSON.stringify({ status, input, reasons }, null, 2));
if (status !== "PASS" && !reportOnly) process.exitCode = 2;
