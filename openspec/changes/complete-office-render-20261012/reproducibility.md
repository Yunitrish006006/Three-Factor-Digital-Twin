# Reproducibility

Canonical school checkout at start 500a9ac. Runtime package and official checksum are recorded after actual resolution. Execute scripts/render_thesis_office.py with explicit --soffice and --output paths in a temporary, isolated runtime; generate page derivatives using Poppler or the packaged document renderer where it functions. User installation/profile remains untouched. Large per-page images may be retained as reproducible temporary derivatives; committed evidence contains full-page hashes, selected observations and contact sheets covering the complete page set.

Inspect exact final Office inputs after all rebuilds; verify recorded coverage and hashes with scripts/verify_office_render.py. Then run applicable native builders and existing delivery/thesis/OpenSpec checks. No run_all_thesis_experiments.py, frozen enclosure runner or E15 execution. Commit/push meaningful validated stages and verify live remote SHA.
