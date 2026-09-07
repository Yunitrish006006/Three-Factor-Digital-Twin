# Design

## Prediction Structure

For each target sensor and complete minute, all predictions exclude that target. The role-local estimate uses only same-role peers and spatial weights. The hierarchical estimate partially pools this local estimate toward the same-role mean, reducing sensitivity to a single neighbor while retaining role semantics.

## Development and Confirmation Separation

E11E is allowed to select from the finite preregistered grid. The selected model ID and complete formula must be frozen in evidence before any E11F request. E11F then evaluates only that model and the frozen stronger-baseline definition.

## Failure Policy

Range overlap, non-206 response, hash or byte mismatch, incomplete metadata, fewer than 42 sensors, no complete snapshots, or empty same-role peer sets aborts the run without selecting a candidate.

