# Research Framing

## Problem and Gap

The project currently demonstrates low field-estimation error, but numerical precision is not itself an application requirement. Human-comfort decisions commonly use target bands and tolerances, so a sub-degree estimator does not prove that equally precise actuation is useful. The next application direction must require dynamic temperature, humidity, and light profiles while remaining inside the model's evaluated `20–30 °C` domain.

At the method level, the public benchmark lacks a recurrent comparator even though the task is temporal. At the state-estimation level, the project has not yet evaluated Kalman filtering, although greenhouse studies show both useful online parameter adaptation and cases where EKF/UKF/MA filtering failed when the underlying climate model was inaccurate.

## Research Questions

| ID | Question | Type | Capability |
| --- | --- | --- | --- |
| `RQ-RNN-01` | 在完全相同資料列、四步歷史、target、chronological split 與 test rows 下，vanilla RNN 相對 persistence、sequence linear regression 與本研究 physics-structured readout 的 MAE 分布為何？ | exploratory | `evaluation-and-evidence` |
| `EQ-APP-01` | 哪一類需要動態精準溫濕度／照度配方的封閉環境，同時符合目前 `20–30 °C` 範圍與單房間稀疏感測架構？ | exploratory | `research-governance` |
| `EQ-KF-01` | Kalman-family methods較適合放在量測去噪、隱狀態估測、感測融合，或 physics-model 線上參數調整的哪一層？ | exploratory | `hybrid-residual-learning` |

## Hypotheses

No directional RNN superiority hypothesis is registered. The professor-requested comparison is descriptive, and every loss must be retained. Application fit and Kalman placement also remain exploratory until task-specific data are collected.

## Construct Operationalization

| Construct | Operational definition | Unit / scale | Source |
| --- | --- | --- | --- |
| fair comparator data | identical normalized SML2010 rows, four consecutive origin records, eligibility mask, chronological split, targets, and test endpoints | row IDs/timestamps | evaluator audit |
| vanilla RNN | one tanh Elman recurrent layer with a fixed pre-registered architecture, trained only on the shared training rows | deterministic model | new evaluator |
| dynamic precision application | programmed setpoint/profile changes in at least temperature plus humidity or light, with a reason to track transient state rather than only a broad comfort band | categorical matrix | primary literature |
| in-domain application | every intended indoor operating/target temperature lies within `20–30 °C`; outdoor boundary inputs do not expand the claim | °C | current model boundary |
| Kalman reference route | future state-space estimator with explicit transition, observation, process-noise, and measurement-noise contracts | protocol status | literature/design note |

## Intended Claims

| ID | Exact bounded claim | Evidence class | Forbidden overclaim |
| --- | --- | --- | --- |
| `CLM-RNN-01` | A fixed vanilla RNN was compared with persistence, sequence linear regression, and a physics-structured readout on identical SML2010 S2 sequence endpoints; case-level wins and losses are preserved. | public task-aligned | universal RNN superiority; different-data ranking; full 3-D validation |
| `CLM-APP-01` | Dynamic controlled-environment plant growth within `20–30 °C` is a plausible candidate application because published studies program temperature/humidity/light profiles, but current project evidence does not validate plant outcomes or all required variables. | literature-grounded direction | current deployment readiness; applicability beyond 20–30 °C; biological efficacy |
| `CLM-KF-01` | Kalman filtering is a relevant future reference for state/parameter estimation, with performance contingent on model and noise assumptions; no project advantage is yet evaluated. | literature/design | completed Kalman experiment; guaranteed denoising benefit |

## Application-Fit Criteria

Candidate applications are ranked only if they satisfy all of the following:

1. They require time-varying environmental recipes rather than only a constant room setpoint.
2. Temperature, humidity, and light are relevant controlled or monitored variables.
3. All intended indoor operating and target temperatures lie within `20–30 °C` for the first project-aligned scenario; external weather input may differ but does not expand the indoor claim.
4. Spatial non-uniformity or sparse sensing plausibly matters.
5. Missing variables and biological/process endpoints are explicitly listed.

The current leading candidate is a closed plant growth chamber or small plant-factory module using day/night or growth-stage recipes inside `20–30 °C`. It remains a direction, not an accepted deployment claim.

## Literature Grounding

- Elman (1990), *Finding Structure in Time*, DOI `10.1207/s15516709cog1402_1`: recurrent links provide dynamic memory; used only to define the vanilla RNN family.
- Chiang, Bånkestad, and Hoch (2020), *Reaching Natural Growth*, DOI `10.3390/plants9101312`: controlled growth facilities compared fixed, sinusoidal, and field-tracking temperature/humidity/light profiles and found that environmental fluctuation affects plant performance.
- Kim et al. (2023), *Preventing Overgrowth of Cucumber and Tomato Seedlings Using Difference between Day and Night Temperature in a Plant Factory with Artificial Lighting*, DOI `10.3390/plants12173164`: demonstrates programmed day/night temperature and light conditions, but some treatments fall outside `20–30 °C` and therefore cannot be adopted unchanged.
- van Mourik et al. (2019), *Improving climate monitoring in greenhouse cultivation via model based filtering*, DOI `10.1016/j.biosystemseng.2019.03.001`: EKF/UKF/moving-average filtering did not generally improve monitoring; performance depended strongly on model accuracy.
- Speetjens, Stigter, and van Straten (2009), *Towards an adaptive model for greenhouse control*, DOI `10.1016/j.compag.2009.01.012`: EKF-based online parameter adaptation improved a time-varying greenhouse model, supporting future parameter/state-estimation study rather than guaranteed filtering benefit.

## Competing Explanations and Validity Threats

- RNN improvement may come from its history window rather than recurrence; sequence linear regression receives the same window to test this alternative.
- Persistence may remain strongest because indoor variables have high temporal inertia.
- The physics readout has a structural prior even when learned checkpoints are disabled; fairness means equal observed data, not identical inductive bias.
- SML2010 is a residential two-point dataset, not a plant chamber.
- Human comfort, plant performance, and laboratory process quality have different endpoints and tolerances.
- Lux is not equivalent to plant PPFD/PAR; cultivation transfer requires a new light-sensing contract.
- `20–30 °C` is a current operating boundary, not proof of coverage at every value or transient within that interval.

## Ethics, Privacy, Safety, and Licensing

- No new human-subject or occupancy data are introduced.
- SML2010 provenance and license remain unchanged.
- No physical control or biological experiment is executed in this change.
- Future cultivation tests must define plant material, biosafety, actuator limits, and environmental endpoint ethics where applicable.
