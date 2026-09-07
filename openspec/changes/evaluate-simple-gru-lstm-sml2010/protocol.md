# Pre-Registered Protocol

## Dataset and task

- Dataset: normalized SML2010 S2 already stored under
  `outputs/data/normalized_public/sml2010/`.
- Horizons: 15, 60, and 1440 minutes.
- Targets: dining temperature, room temperature, dining humidity, and room
  humidity, for 12 cases total.
- History: four consecutive origin records at 15-minute cadence.
- Split: chronological 70% train and 30% test after shared history exclusions.
- Standardization: train rows only; the same transformed sequences are supplied
  to every recurrent model.

## Fixed recurrent configurations

| Model | Hidden units | Approximate parameters |
|---|---:|---:|
| Vanilla Elman RNN | 6 | 148 |
| GRU | 3 | 169 |
| LSTM | 2 | 140 |

All models use one joint four-target output, 30 epochs, batch size 32, Adam
learning rate 0.01, gradient clipping at 1.0, and seed 42. There is no early
stopping, architecture search, or test-based model selection.

## Comparators and metrics

Retain persistence, sequence linear regression, and the physics-structured
readout. Report per-case MAE, RMSE, and maximum absolute error for all six
methods; lowest-MAE counts; GRU/LSTM wins against vanilla RNN; per-case relative
MAE reduction; median relative reduction; parameter counts; training loss; and
wall-clock training time.

## Data-parity and failure rules

- Every method must share the existing train/test endpoint and input hashes.
- All 12 cases and three horizon audits must be present.
- Every training loss and prediction must be finite.
- A missing comparator, hash mismatch, or non-finite run yields
  `NOT_EVALUATED`; partial rankings are not reported as evidence.
- Preserve all adverse and null results without changing hidden units, epochs,
  seed, history, horizons, or files.

## Decision rule

H-RNNGATE-01 is supported only if GRU or LSTM beats vanilla RNN in at least
8/12 cases and its median per-case relative MAE reduction is greater than 0%.
This forwards a candidate only; it is not a general superiority claim.

## Output

`outputs/data/public_benchmarks/gru_lstm_sml2010_comparison.json`
