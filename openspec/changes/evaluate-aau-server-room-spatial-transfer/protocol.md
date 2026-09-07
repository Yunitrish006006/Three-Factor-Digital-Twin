# Protocol

## Source and Provenance

- Dataset: AAU server-room dataset v4, DOI `10.5281/zenodo.19398358`.
- Main file: `AAU_temperature_and_power_use.csv`, 706,160,545 bytes, MD5 `fdb84fef0733db5a0a9564e028725494`.
- Geometry sources: `AAU_DC_geometry_with_measurement_points.log`, annotated temperature figures, and room plan.
- Raw files remain outside the repository under `/tmp`.

## Coordinate Mapping

- Convert CAD millimeters to meters.
- Shift CAD `x` and `y` by the annotated room minimum of 100 mm so the research room origin is the floor southwest corner.
- Use room dimensions `4.20 m x 5.72 m x 3.00 m`.
- Include 42 rack-front, rack-back, and vertical-gradient PT100 channels with unambiguous mapping.
- Exclude six cooling-wall/window channels because their left/right pairing is not machine-readable and has not been independently verified.

## Deterministic Sampling

- Request 12 byte ranges of 4 MiB each, evenly spaced from byte 0 through the final valid 4 MiB start offset.
- Keep the header from the first range; prepend it when parsing later ranges.
- Discard the first partial record of nonzero-offset ranges and the final partial record of every range.
- Parse timestamp, three power channels, and the 42 registered temperature channels.
- Aggregate duplicate and high-frequency records into one-minute medians within each range.
- Deduplicate minute timestamps after concatenation.
- Require all 42 temperatures to be finite for a snapshot to enter the primary evaluation.

## Evaluation

For every eligible one-minute snapshot and every sensor, hide that sensor and predict it from the other 41 sensors using:

1. `global_mean`: arithmetic mean of observed temperatures.
2. `nearest_neighbor`: value at the nearest 3D coordinate, with channel name as deterministic tie-breaker.
3. `idw_3d_p2`: inverse-distance weighting with fixed `p=2` and epsilon `1e-12`.

## Metrics

- Per-sensor and macro MAE, RMSE, and P95 absolute error.
- Count and fraction of sensors for which each method has lowest MAE; ties within `1e-12` count for every tied method and are disclosed.
- Snapshot count, excluded-row counts, observed time range, and power summary.
- No hyperparameter search after metric inspection.

## Evidence Rule

`evidence.md` SHALL be created only from actual output. Null, adverse, failed, partial, and missing results SHALL remain visible.
