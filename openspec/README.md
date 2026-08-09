# Research OpenSpec

This directory is the canonical OpenSpec workspace for the thesis project.
`../OPEN_SPEC.md` is only a short compatibility entrypoint; the testable
research and system contracts live here.

## Directory map

```text
openspec/
├── config.yaml
├── schemas/research-first/
├── specs/
├── changes/
│   ├── archive/
│   └── <active-change>/
└── README.md
```

- `specs/` describes what the project currently supports and what the current
  evidence is allowed to claim.
- `changes/` contains proposed research or implementation changes.
- `schemas/research-first/` defines the project-specific artifact workflow.
- `config.yaml` injects the thesis scope and synchronization rules into every
  OpenSpec artifact.

## Research-first workflow

```text
proposal
  -> research
  -> protocol
  -> specs
  -> design
  -> reproducibility
  -> tasks
  -> implementation / experiment
  -> evidence
  -> synchronized rebuild
  -> archive
```

The `evidence` artifact is intentionally written after an experiment or
implementation has produced auditable outputs. A completed planning folder
without `evidence.md` is therefore still an active change.

## Stable identifiers

Use these prefixes when adding material:

| Prefix | Meaning | Example |
| --- | --- | --- |
| `RQ` | Research question | `RQ1` |
| `H` | Confirmatory hypothesis | `H1` |
| `EQ` | Exploratory question | `EQ1` |
| `CLM` | Publishable claim | `CLM-EVAL-01` |
| `E` | Experiment or validation item | `E8` |
| capability prefix | OpenSpec requirement | `EVD-004` |

Requirement IDs must be unique across `openspec/specs/`. Existing IDs are
checked by `python3 scripts/validate_research_openspec.py`.

## Starting a research change

With the OpenSpec CLI installed:

```bash
openspec new change <kebab-case-name>
openspec status --change <kebab-case-name>
openspec instructions proposal --change <kebab-case-name>
```

The project default is `research-first`, so no `--schema` flag is required.
The files remain usable without the CLI: copy the templates from
`schemas/research-first/templates/` into a new change folder and follow the
dependency order in `schema.yaml`.

## Validation

Repository-local structural validation:

```bash
python3 scripts/validate_research_openspec.py
```

If the OpenSpec CLI is available, also run:

```bash
openspec schema validate research-first
openspec validate --all
```

Research result verification is separate:

```bash
python3 scripts/verify_thesis_results.py
```

## Change closure

A research change is ready to archive only when:

1. all `tasks.md` items are checked;
2. `evidence.md` records actual outputs and deviations;
3. every affected claim has an explicit support decision;
4. tests and result verification pass;
5. all synchronized thesis, IEEE, presentation, figure, and generated outputs
   are rebuilt where applicable;
6. stale claims and metrics have been searched across the repository.

Archive paths use `changes/archive/YYYY-MM-DD-<change-name>/`.
