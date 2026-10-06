# Candidate design

E-ENC-31 / ENC-301: isolated `digital_twin/control/sparse_enclosure.py`, source→plate→air→inlet plus bypass and measured fan delay. Heat exchange between source/plate and plate/air is equal and opposite. All equations are this project's mathematical organization; no invented literature equation numbers.

RQ-ENC-31 / ENC-302: estimate three thermal states using a physics predictor and linear measurement update for plate/air; source is held out. Per-rig bounded two-parameter identification uses sparse calibration only. Learning an MLP or disturbance model is deferred; no three-factor production replacement.

RQ-ENC-32 / ENC-303: shared command limiter, PI/PID and finite candidate ranker. Quadratic stage costs borrow optimal-control reasoning; ranker is neither LQR nor complete MPC QP. Ranking horizon/observation ablations isolate mechanisms. Truth resides in runner only, and metrics are independently recomputed from CSV.

Failure paths: nonfinite inputs reject; failed calibration reverts to nominal and reports status; no source-truth protection oracle; observer warning override bounded by same slew. No hardware API. Synchronize evidence-derived supplement via one summary module into existing builders and report generator. Preserve unrelated worktree changes and use scoped commits.
