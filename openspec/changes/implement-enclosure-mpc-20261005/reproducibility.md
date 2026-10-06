# Reproducibility

Python 3.11、NumPy 1.26.4、SciPy 1.14.1；專用 `.venv-mpc`。原 `.venv` 綁定 Xcode Python，目前因 license 無法啟動，故另建環境，不改其設定。

```sh
/opt/homebrew/bin/python3.11 -m venv .venv-mpc
.venv-mpc/bin/python -m pip install -r scripts/enclosure_mpc_requirements.txt
.venv-mpc/bin/python -m unittest tests.test_enclosure_mpc
.venv-mpc/bin/python scripts/run_enclosure_mpc.py --phase calibrate
.venv-mpc/bin/python scripts/run_enclosure_mpc.py --phase evaluate
.venv-mpc/bin/python scripts/verify_enclosure_mpc.py
.venv-mpc/bin/python scripts/validate_research_openspec.py
```

Clean reruns use `--output-dir /private/tmp/<new-directory>` for both phases and verification to preserve registered artifacts. Source commit, dirty state, effective config, environment, command, source/trace SHA-256, search candidates, selection scores, split seeds, complete rows and actual timestamps are recorded. Source changes invalidate a freeze. No external dataset, proprietary FMU or physical measurements. Package source license remains upstream; locally authored scenario values are assumptions.
