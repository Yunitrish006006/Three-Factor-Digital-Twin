# Research Questions and Claims

## RQ-ENC-03

On AAU Server Room v4 records disjoint from E11B discovery ranges, does fixed local three-neighbor IDW improve held-out-location temperature reconstruction over the E11B-winning one-nearest-neighbor baseline?

## H-ENC-03

Local 3-D IDW with `k=3` and `p=2` will reduce both macro MAE and RMSE relative to one-nearest-neighbor interpolation, obtain lower per-sensor MAE for at least 26 of 42 sensors, and have a positive lower bound for the 95% day-block-bootstrap interval of paired MAE improvement.

## Rationale

- Global IDW can smooth local variation; local variants restrict interpolation to a fixed nearest-neighbor set. This is consistent with the local-neighborhood formulation described in Li et al., *Fast Inverse Distance Weighting-Based Spatiotemporal Interpolation* (2014), https://pmc.ncbi.nlm.nih.gov/articles/PMC4199009/, and Xiao et al., *Fast k-Nearest-Neighbors Calculation for Interpolation of Radar Reflectivity Field* (2009), https://journals.ametsoc.org/view/journals/atot/26/7/2009jtecha1234_1.xml.
- Data-center interpolation has previously compared IDW and kriging, but that task and sensor layout are not treated as interchangeable with AAU: Oktavia et al. (2016), doi: `10.1109/ICITISEE.2016.7803050`.
- Rack cooling may include recirculation and bypass, so Euclidean distance remains only a baseline rather than an airflow model: Tong et al. (2023), doi: `10.1016/j.applthermaleng.2023.120737`.

## Claim Boundary

A supported H-ENC-03 would establish only that a fixed local Euclidean neighborhood improves this disjoint sampled AAU leave-one-sensor-out task. A negative decision remains informative and does not authorize tuning on the confirmation ranges. Neither outcome identifies airflow causally or validates explicit rack topology.

## Competing Explanations and Threats

- Nearest neighbor may remain optimal because front/back and vertical strata are sharply separated.
- Three neighbors may cross rack or aisle boundaries and add bias.
- Fixed byte ranges sample the file rather than the full deployment period.
- Day-block bootstrap reflects sampled-day variability, not independent data-center deployments.
- Six ambiguous cooling-unit channels remain excluded using the E11B mapping rule.
