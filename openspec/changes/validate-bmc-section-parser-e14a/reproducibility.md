# E14A Reproducibility

- Python standard library only.
- Exact frozen manifest and raw hashes required.
- Production parser and oracle SHALL be separate functions in separate files.
- Synthetic tests SHALL include multiple `#group` sections and a host section whose row width can match a BMC header.
- Machine-readable output SHALL include every file count, mismatch, gate, accepted extrema, and the known-row exclusion result.
