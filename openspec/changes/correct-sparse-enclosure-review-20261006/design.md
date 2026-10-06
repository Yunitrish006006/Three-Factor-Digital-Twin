# Design

ENC-401 uses a versioned subclass with required raw observations; source/plate/air predictor and optimizer remain frozen imported primitives. New replay entrypoint supplies measured channels. Legacy source remains available solely to reproduce historical E-ENC-31.

ENC-402 adds a scorer-side audit independent of input-only legacy replay, using scipy integration of written heat balances and exact fan dynamics. A historical Git-byte manifest is an additional integrity anchor, not a substitute for time/dynamics checks. Test negative fixtures independently of legacy metric assertions.

SYN-401 replaces hardcoded observed_qa in sync script with a separate immutable observation store and current hash status. Validation may read but not create observations. Synchronize evidence-derived correction/capacity wording with existing summary helpers.

ENC-403 solves conductance steady balance and labels capacity analysis retrospective. No control gain, target or model coefficient tuning. All actual source/observation roles remain distinct.
