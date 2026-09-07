# Pre-Registered Protocol

## Protocol Identity

- Change: `execute-equipment-enclosure-transfer`
- Protocol version: `1.0.0`
- Registration date: `2026-08-23`
- Related IDs: `RQ-ENC-01`, `RQ-ENC-02`, `H-ENC-01`, `CLM-ENC-01`, `E11A`
- Status: `PLANNED`

## Experimental Design

- Study type: retrospective public-dataset temporal comparison。
- Unit of analysis: one source trace and one `device_id`。
- Experimental unit: one adjacent valid current/next observation pair。
- Number of runs or samples: all eligible pairs from at least three independently labelled traces。
- Conditions and controls: identical rows, target, split and metrics for every comparator。
- Randomization or chronological ordering: no shuffle；chronological 60/20/20 split per case。
- Blinding, if applicable: not applicable；thresholds are fixed before data execution。

## Variables

| Role | Variable | Definition | Unit | Collection source |
| --- | --- | --- | --- | --- |
| independent | inlet/outlet difference | current inlet minus current outlet | °C | BMC |
| independent | total PSU power | available PSU total-power fields summed | W | BMC |
| independent | mean fan speed | mean of available chassis/PSU fan fields | RPM | BMC |
| dependent | next outlet temperature | next adjacent valid `Outlet_Temp` | °C | BMC |
| control | current outlet temperature | persistence state | °C | BMC |
| confounder | workload/fan mode/cadence | trace metadata and observed interval | categorical/seconds | dataset inventory/CSV |

## Inputs, Sampling, and Provenance

- Room/scenario: one physical server enclosure represented by each BMC `device_id`; no 3-D geometry claim。
- Sensor topology: BMC inlet, outlet, fan and PSU channels；not equivalent to eight room-corner sensors。
- Sampling cadence: preserve observed cadence；pairs with gaps greater than 3× the case median positive cadence are excluded。
- Settling interval: none inferred；trace starts remain included and limitation is reported。
- Dataset source and license: `https://github.com/arealuser/bmcdata`, MIT license, exact commit/checksum recorded at run time。
- Inclusion criteria: parseable timestamp, inlet, outlet, at least one fan field, at least one PSU total-power field, and current/next inlet/outlet all within 20–30 °C。
- Exclusion criteria: missing/non-finite required values, non-positive time order, excessive gap, or out-of-domain air state。
- Missing-data handling: exclude affected pair and report count；no interpolation。
- Outlier policy: no statistical outlier deletion；physical-domain exclusions only。

## Leakage and Contamination Controls

- Train/test split: first 60% train, next 20% validation, final 20% test within each case。
- Time ordering: source timestamps sorted within `device_id`; no future feature enters a current row。
- Repeated-measure handling: report case metrics separately；do not treat rows as independent replications。
- Hyperparameter selection: ridge fixed at `1e-3`; no test-set tuning。
- Prohibited post-outcome adjustments: no trace deletion based on model ranking and no change to domain, split or success threshold after metrics are observed。

## Baselines and Ablations

| ID | Comparator | Purpose |
| --- | --- | --- |
| `B-ENC-P` | persistence | minimum temporal baseline |
| `B-ENC-LR` | standardized linear readout over inlet, outlet, power, fan | generic data-driven baseline |
| `M-ENC-TB` | thermal-balance delta readout over temperature difference, power, and fan×difference | interpretable reduced-order candidate |

## Metrics and Decision Criteria

| Hypothesis / claim | Metric | Success / interpretation rule | Failure rule |
| --- | --- | --- | --- |
| `H-ENC-01` | case-level test MAE | at least 3 eligible cases and `M-ENC-TB` beats persistence in more than half | fewer than 3 cases or wins not above half |
| `CLM-ENC-01` | MAE, RMSE, win counts | report every comparator and adverse case | any row mismatch or hidden failed case invalidates ranking |

## Analysis

- Aggregation: case-level values and win counts；no pooled row-level significance claim。
- Uncertainty or interval estimate: descriptive metrics in `E11A`; later bootstrap must respect trace blocks。
- Statistical test, if justified: none pre-registered for this first transfer screen。
- Multiple-comparison handling: all three methods remain visible per case。
- Sensitivity analysis: report in-scope ratio and median cadence；future versions may pre-register alternate horizons。

## Execution and Evidence Contract

| Step | Command | Expected machine-readable output |
| --- | --- | --- |
| 1 | `python3 scripts/run_enclosure_bmc_baseline.py <trace.csv> [<trace.csv> ...]` | `outputs/data/enclosure/enclosure_bmc_baseline.json` |
| 2 | `python3 -m unittest tests.test_enclosure_bmc_baseline` | test status |
| 3 | `python3 scripts/validate_research_openspec.py` | OpenSpec validation status |

## Deviations and Failure Reporting

- All deviations SHALL be recorded in `evidence.md` after actual public-data execution。
- Failed, missing, insufficient-scope, or contradictory results SHALL remain visible。
- A threshold change after observing results SHALL create a new protocol version。
