# Active Research Changes

Each active change gets one kebab-case directory under this folder and uses the
`research-first` schema defined in `../schemas/research-first/schema.yaml`.

There are no active changes at initial OpenSpec baseline creation. Existing
unverified work, such as `E8` real-room action intervention validation, remains
a documented evidence gap in the current specs and is not silently treated as
an approved or running experiment.

When work on an evidence gap actually begins, create a change folder and follow
this artifact order:

```text
proposal.md
research.md
protocol.md
specs/<capability>/spec.md
design.md
reproducibility.md
tasks.md
evidence.md  # only after execution produces evidence
```

Include a `.openspec.yaml` file containing:

```yaml
schema: research-first
```
