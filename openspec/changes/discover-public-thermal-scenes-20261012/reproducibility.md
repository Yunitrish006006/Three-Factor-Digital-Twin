# Reproduction

Canonical school checkout and .venv-mpc. Save actual availability commands/status/output/source hashes in artifacts/readiness.json and logs. External builds/downloads remain under /private/tmp; source identifiers and exact example commands allow reproduction. Record platform/compiler/package versions actually used. Do not execute frozen study runners or E15.

Build current HTML with scripts/build_professor_report_20261012.py; isolated headless Chrome/Playwright is an explicit fallback, not in-app Browser. Record current exact artifact/evidence hashes after actual screenshot/PDF inspection. Run OpenSpec, existing thesis-result checks and current delivery checks; full unit suite if executable project script behavior changes. Commit/push authorized checkpoints and verify fresh fetched origin/main.

## Exact functional checks actually used

HotSpot official source commit f18831e48cef5d62580585cca0d7fab6c71bc3cc; build `make hotspot`, then from its `examples/example1` directory:

```sh
../../hotspot -c example.config -f ev6.flp -p gcc.ptrace -materials_file example.materials -model_type block -steady_file readiness_outputs/gcc.steady -o readiness_outputs/gcc.ttrace
```

The writable readiness_outputs directory was created before that command. It is the first functional simulation from the supplied run.sh, with distinct output paths and unchanged inputs; the script's second warmup run/cleanup and optional detailed package command were not executed. Verify numeric output with `numpy.loadtxt(path,skiprows=1)`, shape(100,30) and isfinite; do not interpret this as a new controller benchmark.

TCLab source commit a975c36d68ccbc3c0f6dade4ae99c0abc3271f81; source import plus temporary pyserial3.5, no project environment installation. With random.seed(612810), use TCLabModel(synced=False), reset tstart/tlast=0, set Q1(40)/Q2(20), call update(float(t)) for t in range(0,301,30), read T1/T2/Q1/Q2 and close with the normal context manager. Require finite readouts and endpoint response, retaining quantized/noisy values. No controller compared.

BOPTEST: `curl -sS --max-time 20 -D headers.txt -o body.txt https://api.boptest.net/testcases`; retain exit6 DNS error after same approved-network retry, no insecure TLS workaround.

Report verification: `.venv-mpc/bin/python scripts/verify_enclosure_structure_delivery.py` now follows this stage's exact observations; its output stays in this stage rather than overwriting prior artifacts. All original artifact hashes are checked against historical_manifest.json. The full tests/thesis/OpenSpec/QA commands and actual outputs are in evidence.md and artifacts. The PDF skill's authoring marker was executed immediately before the first print-PDF edit; no Office renderer used.
