# Research framing

## Research Questions
- `RQ-RAO-01`: Can deterministic complexity scoring select bounded orchestration without exceeding agent budgets?
- `RQ-RAO-02`: Can structured claim-evidence relations prevent unsupported or contradiction-dropping synthesis states?
- `RQ-RAO-03`: Can independent review be represented as a separate post-synthesis gate?

## Hypotheses
- `H-RAO-01`: fixed task fixtures produce stable orchestration modes and remain within configured subagent budgets.
- `H-RAO-02`: a claim with zero supporting evidence fails validation.
- `H-RAO-03`: contradictory evidence registered for a claim cannot be omitted silently.
- `H-RAO-04`: Evidence Extractor cannot perform final synthesis and Independent Reviewer cannot participate in original synthesis.

## Claim Boundary

Passing these tests demonstrates software enforcement of research-process invariants. It does not demonstrate that a particular multi-agent configuration improves scientific correctness, recall, or real-world research quality.

## Threats
- Complexity factors can still be misclassified before deterministic scoring.
- Structural validation cannot by itself verify semantic correctness of evidence interpretation.
- Source discovery quality remains connector-dependent and is out of Phase-1 scope.
