# Proposal: Pure RNN 3-D Field Comparator

## Research Gap

目前教授要求的 vanilla RNN 只在 SML2010 時序預測子任務完成，尚未在本研究的完整 3-D 場重建任務與 IDW、base model、LOO hybrid 使用相同八情境資料比較。因此既有 RNN 結果不能回答 pure RNN 是否能由八顆稀疏感測器重建目前的三因子空間場。

## Current and Proposed State

- Current: 3-D 場比較只有 IDW、設備感知 base model 與 LOO hybrid residual；vanilla RNN 是獨立的 public time-series comparator。
- Proposed: 新增不使用 physics estimate 的 pure Elman RNN，以固定順序讀取相同八顆角落感測器，對每個查詢點直接預測 temperature、humidity、illuminance，並在相同八個 leave-one-scenario-out folds 報告 full-field MAE。
- Primary estimator remains reduced-order physics. Pure RNN is an evaluation baseline and SHALL NOT silently replace the deployed estimator.

## Claim Impact

This is claim-strengthening only for comparison completeness. A completed result supports a bounded same-task controlled-simulation comparison regardless of whether RNN wins. It does not create real-room dense truth, cross-room generalization, or a claim that recurrent models are inherently superior.

## Affected Synchronized Artifacts

- `openspec/specs/hybrid-residual-learning/spec.md`
- `openspec/specs/evaluation-and-evidence/spec.md`
- `openspec/specs/artifact-synchronization/spec.md`
- `docs/thesis/thesis_draft_zh.md`
- `scripts/build_thesis_docx.py`
- Chinese thesis DOCX/PDF outputs and mirrored outputs
- `docs/papers/ieee/paper.tex`
- `docs/papers/ieee/paper.pdf`
- `scripts/build_thesis_pptx.py`
- both presentation outlines and PPTX outputs
- field-comparison figures and professor report/demo

No submission logistics or personal development notes will be added to professor-facing artifacts.
