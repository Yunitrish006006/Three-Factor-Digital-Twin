# Proposal: Evaluate AAU Local Spatial Transfer

## Motivation

E11B showed that global 3-D IDW improved on a global mean but lost to one-nearest-neighbor interpolation. This result motivates a new, independently evaluated question: can a fixed local neighborhood retain rack-local information while reducing the variance of copying one sensor? Because the model choice was informed by E11B, E11C uses byte ranges that do not overlap the E11B ranges.

## Scope

- Evaluate fixed three-neighbor inverse-distance weighting (`k=3`, `p=2`).
- Compare it with one-nearest-neighbor and global 3-D IDW on the same held-out sensors and minutes.
- Use 11 preregistered gap-centered byte ranges from AAU Server Room v4, one inside each gap between adjacent E11B ranges.
- Preserve bootstrap uncertainty, adverse results, exclusions, and provenance.

## Non-goals

- No parameter selection from E11C confirmation metrics.
- No claim that Euclidean locality represents rack connectivity or airflow topology.
- No CFD, causal cooling-control, energy-saving, component-hotspot, or arbitrary-data-center claim.
- No redistribution of source fragments.

## Completion Criteria

- [x] H-ENC-03, offsets, methods, metrics, and decision rule are fixed before confirmation download.
- [x] The local interpolation implementation and focused tests exist.
- [x] All 11 gap-centered ranges are retrieved and checked for non-overlap.
- [x] Actual evidence and synchronized research artifacts report the result.
