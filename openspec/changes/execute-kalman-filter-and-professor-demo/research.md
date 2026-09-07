# Research Framing

## Research Question

| ID | Question | Type |
| --- | --- | --- |
| `RQ-KF-01` | 在固定的受控量測雜訊下，scalar linear Kalman filter 相對 raw noisy observation 與 causal moving average，能否在相同 SML2010 current-time test rows 降低溫濕度 MAE？ | exploratory |

## Hypotheses

No directional superiority hypothesis is registered. `CLM-KF-02` requires an executable, parity-audited comparison, not a favorable Kalman result. Every method loss and every winning method remain evidence.

## Construct Operationalization

| Construct | Operational definition |
| --- | --- |
| task reference | original normalized SML2010 dining/room temperature or humidity record |
| corrupted observation | task reference plus deterministic zero-mean Gaussian noise generated with the registered seed and target/profile-specific stream |
| raw baseline | current corrupted observation without smoothing |
| moving average | causal mean of the current and previous two corrupted observations within a contiguous segment |
| linear Kalman filter | scalar random-walk state `x_k=x_{k-1}+w_k`, observation `z_k=x_k+v_k`, identity transition and observation matrices |
| data parity | identical corrupted observation hash, chronological split, test timestamps, current-time target, and metric implementation for all methods |

## Noise Profiles

| Profile | Temperature standard deviation | Humidity standard deviation |
| --- | ---: | ---: |
| low | 0.5 °C | 1.5 %RH |
| nominal | 1.0 °C | 3.0 %RH |
| high | 2.0 °C | 5.0 %RH |

These are controlled stress levels, not measurements of a specific deployed sensor.

## Intended Claim

`CLM-KF-02`: A fixed scalar Kalman filter, raw observation, and three-point causal moving average were compared on identical fixed-seed corrupted SML2010 current-time rows under three registered noise profiles. This supports only a controlled filtering-method comparison and does not establish real-sensor, forecast, spatial-field, or control performance.

## Competing Explanations and Threats

- Kalman improvement may come from knowing the injected measurement variance rather than from better physical modeling.
- Moving-average performance depends on the fixed three-row window.
- The random-walk process model can smooth transitions and increase lag.
- SML2010 dining/room points are not the project's eight-corner room topology.
- The original measurement contains unknown sensor and process noise; it is only the task reference used before additional controlled corruption.
- Test cases share one dataset and therefore do not establish cross-site generality.

## Ethics, Privacy, and Safety

The experiment introduces no new human-subject data and actuates no physical device. It reuses the repository's normalized public dataset and preserves its existing provenance and licensing boundary.
