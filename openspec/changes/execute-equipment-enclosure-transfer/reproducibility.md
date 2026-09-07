# Reproducibility Manifest

## Environment

- OS: Linux or macOS。
- Python: 3.9+，standard library plus repository package。
- Dependencies: no new third-party dependency for `E11A` baseline。
- Hardware assumptions: CPU-only；raw dataset storage supplied by runner。
- Timezone and locale: timestamps parsed with recorded timezone when present；run timestamp written in UTC。

## Inputs and Provenance

| Input | Source / license | Version / checksum | Committed? |
| --- | --- | --- | --- |
| BMC traces | `https://github.com/arealuser/bmcdata`, MIT | exact Git commit and per-file SHA-256 at run time | no |
| AAU server-room data | DOI `10.5281/zenodo.19398358` | v4 / published MD5 values | no; future `E11B` |
| HazardNet data | DOI `10.5281/zenodo.10050368` | v1 / published MD5 values | no; secondary |

## Determinism

- Random seeds: none；all fitting and ordering are deterministic。
- Data split: chronological 60/20/20 per source file and `device_id`。
- Ordering: timestamp ascending, then stable source order for equal timestamps。
- Known nondeterminism: none expected after source bytes are fixed。

## Clean-Room Execution Order

```bash
# Acquire selected BMC traces separately and record repository commit.
python3 scripts/run_enclosure_bmc_baseline.py /path/to/bmcdata/data/*.csv
python3 -m unittest tests.test_enclosure_bmc_baseline
python3 scripts/validate_research_openspec.py
```

## Expected Outputs

| Output | Producer | Required keys / invariants |
| --- | --- | --- |
| `outputs/data/enclosure/enclosure_bmc_baseline.json` | `run_enclosure_bmc_baseline.py` | `dataset`, `protocol`, `cases`, `summary`; same split hash for all methods |

## Verification

```bash
python3 -m unittest tests.test_enclosure_bmc_baseline
python3 scripts/validate_research_openspec.py
```

Run the full thesis verification and synchronized rebuild only after accepted evidence changes a registered claim.

## Provenance Record

Future `evidence.md` SHALL record source repository commit, dirty-worktree state, UTC execution time, exact commands, source SHA-256, output hash, trace inventory, exclusions, deviations, failures and claim decisions. Planning and fixture-test output SHALL not be presented as research evidence.
