# Evidence: execute-equipment-enclosure-transfer

## Execution Record

- Execution date: `2026-08-23` Asia/Taipei; machine-readable timestamp `2026-08-23T08:31:45.162419+00:00`.
- Project commit: `ea1d9194c8252e81cae2fe6842fa4064bab97397`; worktree dirty, including this change and pre-existing modifications.
- Dataset: `https://github.com/arealuser/bmcdata`, commit `24904fa9a9bac49a3f6f3198bb04e1be5e2707ea`, MIT License.
- Inputs: 124 CSV files under `data/`; raw files remain outside this repository.
- Command: `python3 scripts/run_enclosure_bmc_baseline.py /tmp/school-bmcdata/data/*.csv`
- Output: `outputs/data/enclosure/enclosure_bmc_baseline.json`
- Output SHA-256: `08eab9291d77698f3ee436b4fe264f48e96b623fb6e4b44c0828d6b78cd1fa26`.
- Per-source SHA-256 and split endpoint hashes are preserved in the JSON.

## Protocol Compliance and Deviations

- The `20–30 °C` domain, chronological 60/20/20 split, ridge `1e-3`, and 30-pair minimum were unchanged.
- An initial six-trace run produced no evaluated cases. The final run used the complete 124-file inventory from the same fixed commit and selected cases only by pre-registered eligibility, not model outcome.
- The first CLI attempt exposed a repository-root import-path defect. The entry point was fixed before the successful run; no model, split, metric, or threshold changed.

## Results

- Total file-device cases: 317.
- `insufficient_in_scope_samples`: 312.
- Evaluated cases: 5; all had 11-second median cadence.
- Thermal-balance wins versus persistence: 0/5.
- Lowest test-MAE counts: persistence 5, linear readout 0, thermal-balance readout 0.
- `thermal_balance_majority_threshold_met`: false.

| Case | Eligible pairs | Persistence MAE | Linear MAE | Thermal-balance MAE | Lowest |
| --- | ---: | ---: | ---: | ---: | --- |
| `202512112333.csv:bmc` | 45 | 0.111111 | 0.611499 | 0.644822 | persistence |
| `202512120002.csv:bmc` | 75 | 0.200000 | 0.236494 | 0.464760 | persistence |
| `202512120114.csv:bmc` | 249 | 0.019608 | 0.075570 | 0.165912 | persistence |
| `202512132226.csv:bmc` | 86 | 0.000000 | 0.086525 | 0.083910 | persistence |
| `202512132302.csv:bmc` | 99 | 0.000000 | 0.027354 | 0.033091 | persistence |

## Adverse and Missing Evidence

- The registered thermal-balance model never beat persistence and never achieved lowest test MAE.
- Two test partitions had constant quantized outlet readings, allowing persistence MAE 0; the other three also favored persistence.
- 312/317 cases lacked 30 eligible 20–30 °C pairs, preventing broad enclosure applicability.
- BMC data provide no dense 3-D enclosure geometry or reference field.
- CPU/GPU hotspot, PID effectiveness, causal intervention, and physical deployment were not evaluated.

## Research and Claim Decisions

| ID | Decision | Basis |
| --- | --- | --- |
| `RQ-ENC-01` | answered negatively for this task | thermal-balance beat persistence in 0/5 eligible cases |
| `RQ-ENC-02` | partially explored | short cadence, quantization, and inertia favored persistence |
| `RQ-ENC-03` | planning only | AAU 3-D data remain reserved for `E11B` |
| `H-ENC-01` | **not supported** | the registered majority-win threshold failed |
| `CLM-ENC-01` | bounded negative claim supported | same-data metrics and failures are reproducible |

Accepted statement: within five eligible BMC file-device cases and the registered 20–30 °C next-observation outlet-air task, persistence was lowest-MAE in all five and thermal-balance won none. This does not validate 3-D enclosure transfer, component hotspots, PID, or arbitrary equipment cabinets.
