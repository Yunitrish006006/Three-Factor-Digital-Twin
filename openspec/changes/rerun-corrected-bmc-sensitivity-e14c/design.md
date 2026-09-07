# E14C Design

E14C calls the existing `select_and_refit` and `evaluate_frozen` APIs without adding robust candidates. The only data change relative to E13 is the supported E14B source-aware unit normalization.

The runner records the corrected frozen model before reparsing the already opened retrospective-test files. This preserves execution traceability but does not restore test blindness. Output wording uses eligibility rather than hypothesis support.
