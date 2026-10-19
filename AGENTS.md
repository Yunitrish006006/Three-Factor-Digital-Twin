# Repository Working Rules

## Presentation format preference (user reaffirmed 2026-09-08)

All new professor presentations SHALL be offline-capable HTML webpages, not PPTX.
The user's explicit format preference overrides PPTX output requirements below
for new presentation work. Preserve historical PPTX files; do not rebuild them
solely for a new exploratory professor briefing. Keep candidate application
proposals visibly separate from adopted thesis methods and completed evidence.

This repository contains one research project expressed in multiple synchronized artifacts. Any AI assistant editing this repository must treat the following outputs as one coupled deliverable, not as independent documents.

## Current research and submission focus (confirmed 2026-10-19)

- **Active:** compare actual closed-loop thermal control performance of algorithms in an enclosure model (PI/PID/LQR/MPC etc.), diagnose the causes of performance differences, and optionally devise/test a stronger controller. Distinguish *simulated closed loop* from physical PC-enclosure evidence.
- **Near-term submission:** Chinese conference review manuscript at `docs/papers/conference_review_2026-10-19/manuscript_zh.md`; **CSME 2026 is a candidate, not yet professor-approved, submitted, or accepted**. Student prefers Chinese per advisor. See `docs/planning/2027-01-graduation-csme2026-zh.md` and `docs/research/current_enclosure_control_scope_2026-10-19_zh.md`.
- **Graduation objective:** January 2027, conditional on advisor/department confirmation of applicable program rules, Chinese acceptance and oral-defense requirements.
- **Historical topics:** room humidity/illuminance/3D reconstruction, Google Home and MCP service exploration are not current headline contributions. Consult `docs/archive/room-spatial-digital-twin/README.md`. Preserve research code and frozen evidence at their original paths.
- Updating an organizational index or calendar alone does not change scientific claims; any scientific thesis refocus/rewrite **does** require the full research-first/OpenSpec and document synchronization workflow below. Do not imply that the old canonical thesis and IEEE draft have already been rewritten.

## Historical IEEE venue note (2026-08-03; inactive)

The former English-paper exploration targeted IoTaIS 2026 (EDAS `https://edas.info/N34817`; then-announced extended full-paper deadline August 10, 2026). This is preserved for provenance only and **is not** the active 2026-10-19 submission target. Previous IEEE Digital Twin 2026 and IEEE DTPI 2026 were also explored. Do not silently restore these as current venues.


## Room Design Data Requirement

Any new room design, room scenario, or room-specific 3D dataset must follow `docs/requirements/room_design_format_requirements_zh.md`.

At minimum, the design must provide:

- A complete room dimension block with `width_m`, `length_m`, and `height_m`.
- A consistent 3D coordinate system using meters and the origin at the floor southwest corner.
- Sensor, zone, device, and furniture coordinates in `{x, y, z}` format.
- Bounding boxes for zones and furniture using `min_corner` and `max_corner`.
- Validation that every point and bounding box stays inside the room dimensions.

Use `docs/templates/room_design_template.json` for new designs and `docs/templates/room_design_standard_room_example.json` as the current reference room.

## Mandatory Synchronization Scope

Whenever the thesis topic, method, experiment setup, metrics, architecture, figures, chapter structure, or conclusions change, the assistant must update all of the following together:

- Chinese thesis source: `docs/thesis/thesis_draft_zh.md`
- Chinese thesis build source: `scripts/build_thesis_docx.py`
- Chinese thesis outputs:
  - `docs/papers/thesis/thesis_draft_zh.docx`
  - `docs/papers/thesis/thesis_draft_zh.pdf`
  - `outputs/papers/thesis_draft_zh.docx`
  - `outputs/papers/thesis_draft_zh.pdf`
- English IEEE paper source:
  - `docs/papers/ieee/paper.tex`
  - `docs/papers/ieee/references.bib`
- English IEEE output:
  - `docs/papers/ieee/paper.pdf`
- Presentation source:
  - `scripts/build_thesis_pptx.py`
  - `docs/thesis/presentation_outline_zh.md`
  - `docs/thesis/presentation_outline_zh_30min.md`
- Presentation outputs:
  - `outputs/papers/thesis_presentation_zh.pptx`
  - `outputs/papers/thesis_presentation_zh_30min.pptx`

If a change affects figures used by the thesis or slides, also update:

- `docs/thesis/system_architecture_diagrams_zh.md`
- `outputs/figures/architecture/*`
- `docs/papers/thesis/assets/*`

## Progress Consistency Rule

Chinese thesis, English paper, IEEE paper content, and presentation must remain at the same project progress level.

This means:

- If a new method is added to one artifact, it must appear in the others where relevant.
- If an old claim is removed or weakened in one artifact, it must be removed or weakened in the others.
- Metrics, scenario counts, benchmark results, and conclusions must not disagree across artifacts.
- Figure captions and slide wording must match the current thesis narrative.
- Placeholder text, outdated names, and deprecated architecture descriptions must be removed from every synchronized artifact, not just one.

## Source-of-Truth Rules

- The Chinese thesis source and `scripts/build_thesis_docx.py` must stay logically aligned.
- `paper.tex` is the source of truth for the IEEE manuscript.
- `scripts/build_thesis_pptx.py` is the source of truth for the presentation.
- Generated outputs must be rebuilt after source changes.
- Do not update only generated files while leaving source files stale.

## Research OpenSpec Workflow

The canonical research specification lives under `openspec/`.

- Read `openspec/config.yaml` and the affected capability files in
  `openspec/specs/` before making a substantive research change.
- Any change to the topic, method, experiment, metric, architecture, figure,
  chapter structure, evidence level, or conclusion must first use a directory
  under `openspec/changes/` with the `research-first` schema.
- Research changes must trace proposal, research questions or hypotheses,
  protocol, delta specs, design, reproducibility, tasks, and post-run evidence.
- Do not create `evidence.md` from expected or invented outcomes. Populate it
  from actual runs and preserve null, adverse, failed, and missing results.
- Do not archive a research change until its evidence decisions and all
  applicable synchronized artifacts are complete.
- Run `python3 scripts/validate_research_openspec.py` after OpenSpec edits.

## Definition of Done

A thesis-related edit is not complete unless all applicable items below are satisfied:

1. The affected Chinese thesis source is updated.
2. The affected English/IEEE source is updated.
3. The presentation source and outlines are updated.
4. Any affected architecture or result figures are rebuilt.
5. The generated `docx`, `pdf`, and `pptx` outputs are rebuilt.
6. No old metrics, names, captions, or claims remain in synchronized artifacts.

## Required Rebuild Commands

After synchronized edits, run the relevant commands:

```bash
python3 scripts/build_architecture_diagrams.py
python3 scripts/build_thesis_docx.py
python3 scripts/build_thesis_pdf.py
python3 scripts/build_thesis_pptx.py
cd docs/papers/ieee && tectonic --keep-logs --keep-intermediates paper.tex
```

If code or service behavior changed, also run:

```bash
python3 -m unittest discover -s tests
```

## Explicit Prohibitions

Do not do any of the following:

- Update only the Chinese thesis and leave the English paper behind.
- Update only the IEEE paper and leave the slides behind.
- Change benchmark numbers in one artifact without propagating them everywhere else.
- Leave placeholders such as fake emails, draft notes, or “should be revised” text in published outputs.
- Keep repository-structure details in thesis figures when the figure is supposed to describe research architecture.

## Short Instruction for Future AI Tools

If you are an AI assistant making thesis-related edits in this repository, assume that:

- Chinese thesis
- English/IEEE paper
- presentation

must always stay synchronized in scope, claims, metrics, and progress.

If you cannot update all of them in the same round, you must explicitly state that the work is incomplete.

## Algorithm generality constraint (user reaffirmed 2026-09-08)

Do not continue single-scenario manual tuning or add case-specific controller exceptions. Existing BOPTEST results are single-FMU exploratory development, not proof of generality. See `docs/research/boptest_generality_audit_2026-09-08_zh.md`. Any resumed improvement SHALL first separate device settings from control logic and specify a shared calibration/selection procedure and held-out-plant evaluation. Per-device automatic identification may use the same predeclared procedure/budget; researchers must not manually choose per-test-device gains, smoothing or exceptions. Freeze algorithms and shared hyperparameters before unseen plants; do not relabel opened dates as unseen. Preserve prior results and source hashes.

### Clarification: bounded cross-scenario adjustment is authorized
The user explicitly allows adjustable parameters and slight per-scenario adaptation, provided the same algorithm and a documented small-data/limited-trial procedure apply across scenarios. Do not interpret the constraint above as forbidding such adaptation. Expose adjustable parameters and count their data/time/trial cost; do not introduce result-driven case exceptions.
