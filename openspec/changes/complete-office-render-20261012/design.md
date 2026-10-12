# Design

SYN-601 introduces an explicit Office render manifest containing input/output/page hashes and runtime provenance; a separate observation record establishes actual visual acceptance. Never allow the rendering script itself to mark pages visually accepted.

SYN-602 fixes only observed layout problems at their source in existing builders; all applicable synchronized outputs are rebuilt. Existing renderer constraints, known initial data and frozen research files remain distinct from formatting changes.

SYN-603 removes a stale artifact-synchronization requirement that still calls completed E15 protocol-only, aligning it to existing EVD-042 completed-confirmation scope. Result metrics and evidence interpretation are not strengthened.
