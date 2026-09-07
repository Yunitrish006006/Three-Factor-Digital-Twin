# E14A Protocol

## Frozen Inputs

- Use the 31 files in `outputs/data/enclosure/bmc_cross_run_e12_manifest.json`.
- Require manifest SHA-256 `9f0ef4e25805af89ac1f59ae1e13f39bf036a510dcbe07f4a2d3ccd4f78cad74`.
- Verify every raw file's byte count and SHA-256 before parsing.

## Production Parser

- Start a new section whenever a raw line begins with `#group`.
- Ignore other comment metadata while retaining section state.
- Treat the first non-comment row in each section as that section's header.
- Consider a section BMC-capable only when its header contains every preregistered BMC field.
- Accept a data row only when its own `_measurement` is `sdgp`, its own `device_id` is `bmc`, its width matches its section header, and all required numeric values are finite.
- Never carry a header across a `#group` boundary.

## Independent Oracle

- Implement a separate raw-line scanner outside the production parser module.
- For each section, identify the local header and count width-matched rows by the literal header positions of `_measurement` and `device_id`.
- Count only rows equal to `sdgp` and `bmc` in a header that contains all required BMC columns.
- Do not call the production parser or its section helper.

## Metrics and Gates

- Report production and oracle counts for every file.
- Require exact agreement for 31/31 files and at least one accepted row per file.
- Require zero accepted non-BMC rows.
- Require the known host timestamp in `202401050043.csv` to be absent.
- Require accepted inlet, outlet, CPU1, CPU2, and target values below 1,000 degrees C.
- Report min/max for temperature, fan, power, thermal-rise, and power-per-fan fields without using them to delete rows.
