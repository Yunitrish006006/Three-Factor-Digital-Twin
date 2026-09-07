# Reproducibility

## Planned Commands

```bash
python3 scripts/download_aau_temperature_ranges_e11e.py
python3 scripts/run_aau_hierarchical_development.py
python3 scripts/verify_e11e_results.py
```

Reruns validate E11C with timestamp-independent content hash `3c6ca841e100358669be193390947d94bce7096ca83da71a2e6b8b90736cd643` and the E11E manifest with `ea5b48eb572ed694ad616cc0d57d867c17dcb6c9657b903a2345af660e596fd5`; historical full-file hashes remain evidence identifiers, not rerun blockers.

## Determinism

The offsets, candidate grid, model ordering, metrics, forwarding gate, bootstrap replicates, and random seed are fixed in `protocol.md`. The manifest records URL, HTTP status, Content-Range, exact byte counts, fragment SHA-256 hashes, and boundary policy.

## Literature Basis

- Wang et al., gappy POD and sensor-layout optimization, DOI `10.1016/j.enbuild.2024.115078`.
- Tong et al., rack-based state-space reconstruction and sensor-layout effects, DOI `10.1016/j.buildenv.2023.110601`.
- Li et al., limited-sensor indoor temperature reconstruction, DOI `10.1016/j.enbuild.2023.113493`.
