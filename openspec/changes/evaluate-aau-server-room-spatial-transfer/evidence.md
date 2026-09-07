# E11B Post-Run Evidence

## Decision

- Hypothesis: `H-ENC-02`.
- Decision: `not_supported`.
- Decision rule: 3D IDW (`p=2`) had to beat both global mean and nearest neighbor in macro MAE and obtain the lowest per-sensor MAE for at least 60% of the 42 eligible sensors.
- Observed outcome: nearest neighbor, not IDW, was the strongest baseline. No interpolation parameter or coordinate was changed after observing this result.

## Provenance and Reproducibility

- Dataset: *Data from the AAU Server Room* v4, DOI `10.5281/zenodo.19398358`.
- Source object: `Server Room Temperature and Power Data.csv`, 706,160,545 bytes.
- Acquisition: 12 preregistered, evenly spaced HTTP byte ranges of 4 MiB each.
- Original-run range manifest hash: `sha256:788fae3174bb79beda69cfd5d5a62dc17544d139fbc994c5ffbe814996143de7`.
- Current range manifest: `outputs/data/enclosure/aau_temperature_ranges_manifest.json` (`sha256:592a08f01c5d7660767f8c2df15a309bdbc390db5b643054700c2b124aae3be6`). It was rewritten on 2026-08-23 by an unintended downloader re-entry that reused all exact-size fragments; offsets and fragment SHA-256 values did not change. See `RDL-015`.
- Room design: `docs/templates/room_design_aau_server_room.json` (`sha256:f657ae817353273eaeb6da9f3653cb741ffc39ddbfb91c377df2bf8ee5bf48e7`).
- Result: `outputs/data/enclosure/aau_spatial_baseline.json` (`sha256:9b0a98dc45d78c4ae8484a40f07d20fbff4950976944c81bb743cc98ad6966ee`).
- Raw range fragments remain under `/tmp/aau_server_room_temperature_ranges` and are not redistributed by this repository.

## Run Accounting

- Fragments: 12; boundary records discarded: 22.
- Rows seen and accepted: 97,735; malformed or non-finite rows: 0.
- Eligible one-minute snapshots: 1,641, spanning sampled records from 2024-09-16 16:58 through 2024-10-02 13:53.
- Eligible sensors: 42 high-confidence PT100 locations; six ambiguous cooling-unit channels were excluded before evaluation.
- Power range across eligible snapshots: 2,223.5--3,313.3 W; median 2,400.5 W.

## Results

| Baseline | Macro MAE (deg C) | RMSE (deg C) | P95 absolute error (deg C) | Per-sensor wins |
|---|---:|---:|---:|---:|
| Global mean | 2.293 | 2.624 | 4.554 | 6/42 (14.3%) |
| Nearest neighbor | **1.175** | **1.411** | **2.579** | **30/42 (71.4%)** |
| 3D IDW, `p=2` | 1.687 | 1.921 | 3.319 | 6/42 (14.3%) |

IDW improved on the global mean but failed both confirmatory conditions: it did not beat nearest neighbor in macro MAE and won only 6 of 42 sensors, below the required 60%.

## Adverse Evidence and Limits

- The negative result indicates that isotropic distance weighting is insufficient for this sampled room-transfer task. Rack-local topology, airflow direction, or thermal stratification are plausible explanations, but this run does not identify a cause.
- The evidence uses fixed byte-range sampling rather than the complete 706 MB object, so it does not establish full-period robustness.
- Coordinate mapping is limited to 42 unambiguous sensor labels. The six excluded channels must not be treated as failed predictions.
- This evaluation supports neither CFD fidelity nor causal or control claims.
- A topology-aware or anisotropic model requires a separate preregistered change; it must not be presented as a repair of this confirmatory run.

## Difficulties Encountered

See `docs/research/research_difficulty_log_zh.md`, especially `RDL-006` through `RDL-012`, for acquisition, schema, mapping, environment, and negative-result interpretation issues.

## Artifact and Validation Record

- Chinese thesis DOCX and PDF, IEEE PDF, and both presentation PPTX outputs rebuilt successfully on 2026-08-23.
- `python3 -m unittest discover -s tests`: 176 tests passed.
- Research OpenSpec validation: 14 spec files, 117 requirements, 228 scenarios, four active changes.
- Room design validation: `docs/templates/room_design_aau_server_room.json: OK`.
- Existing thesis result verification: 89 passed, zero failed, zero missing.
- E11B consistency verification: seven synchronized sources passed.
- Stale E11B `NOT_EVALUATED` search returned no current-source matches.
- Non-fatal PDF portability and layout warnings are retained in `RDL-013`; the initially incorrect E11B verifier schema path and stale registry line are documented and resolved in `RDL-014`.
