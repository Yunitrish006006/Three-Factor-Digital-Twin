# Reproduction

From school/: python3 scripts/build_application_briefing.py

Then: python3 scripts/validate_research_openspec.py and git diff --check.

Output: docs/reports/application_targets_2026-09-08_zh.html and .json manifest. Python standard library only; no network/build dependency. Open HTML directly; arrows navigate, overview shows all slides, notes toggle and print is browser-provided. Source links require network except relative canonical links. Evidence input hash is stored in the manifest; this build does not rerun any experiment.
