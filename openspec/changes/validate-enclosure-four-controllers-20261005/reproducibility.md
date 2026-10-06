# Reproducibility

Python3.11.15/numpy1.26.4/scipy1.14.1/osqp1.0.4；.venv-mpc，固定requirements。原Xcode .venv不改。

```sh
.venv-mpc/bin/python -m unittest tests.test_enclosure_control_v2 tests.test_enclosure_control_v2_audit
.venv-mpc/bin/python scripts/run_enclosure_control_v2.py --phase calibrate
.venv-mpc/bin/python scripts/run_enclosure_control_v2.py --phase evaluate
.venv-mpc/bin/python scripts/verify_enclosure_control_v2.py
.venv-mpc/bin/python scripts/validate_research_openspec.py
```

clean rerun用新 --output-dir，不重開原正式目錄。保存environment/commit/dirty、source/tracehash、每trial walltime、freeze時間、attempt狀態。不使用publicdataset，scenario自行假設；套件沿用上游license。名義参数已知不是系统辨識，實機/E8未評估。
