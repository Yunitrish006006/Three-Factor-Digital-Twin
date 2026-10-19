# Reproduction

First run focused unit tests on non-evaluation fixtures, validate OpenSpec, and commit the protocol/runner. Execute `.venv-mpc/bin/python scripts/run_enclosure_lqr_diagnostic.py` ONCE. Thereafter use `.venv-mpc/bin/python scripts/verify_enclosure_lqr_diagnostic.py` for stored-data audit only. A new independent study needs a new protocol, directory and seeds, not removal of the attempt receipt. Dependencies are the existing numpy/scipy environment; freeze records versions/hashes. Report rebuild/QA commands will be recorded after actual execution.
