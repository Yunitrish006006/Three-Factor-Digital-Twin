# E13 Reconstructed Evidence

## Outcome

The 2026-09-07 reconstruction completed the 10-row pipeline on the frozen 12/5/14 file split, but the result remains `PARSER_INVALIDATED`. It is a diagnostic record, not model-performance evidence.

## Preserved adverse result

- Inlet-offset baseline: pooled MAE/RMSE/P95 4.1169/4.9873/11.0000 degrees C.
- Raw-unit ridge candidate: pooled MAE/RMSE/P95 32.6769/32.9481/37.0389 degrees C.
- Candidate run wins: 0/14.
- Run-block bootstrap interval for macro MAE gain: [-30.7591, -24.5564] degrees C.
- All accuracy gates failed.

The reconstruction explicitly disables the later E14B unit normalization. E14A and E14B subsequently showed that the parser/unit pipeline required section-aware source filtering and powers-of-ten normalization. Therefore these E13 metrics cannot be used to support or reject the corrected candidate.

## Claim boundary

E13 only preserves the failed historical pipeline and motivates the E14 correction chain. It does not establish same-server transfer, model validity, spatial reconstruction, NTC behavior, or control performance.
