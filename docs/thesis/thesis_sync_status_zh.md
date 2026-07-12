# 論文 LaTeX 與 OpenSpec 同步狀態

## 同步日期

2026-07-12

## 已同步檔案

- `docs/papers/thesis/thesis_draft_zh.tex`

## 本次同步內容

本次已將中文論文 LaTeX 主檔從舊版「8-corner sparse field reconstruction」定位，改為目前 OpenSpec 的研究邊界：

- 核心主張改為「家具感知自由空間中的可驗證目標點估計」。
- 保留 8-corner 作為 baseline，不再作為唯一正式部署假設。
- 加入 `S_input`、`S_validation`、`V_target`、`V_pseudo` 的資料角色。
- 加入 `Ω_room`、`Ω_occ`、`Ω_free = Ω_room \ Ω_occ` 的自由空間定義。
- 加入 ESP32-C3 + DHT11 + BH1750 sensing node 設計。
- 加入 8–10 顆以上 furniture-aware node deployment。
- 加入 `input_fan_path` 與 `input_fan_shadow_zone` 的電風扇感知部署概念。
- 加入 occupancy 作為 dynamic heat / moisture / obstruction source。
- 加入 Google Home UI operation events 作為 operator-verified operation context。
- 明確區分 synthetic full-field、synthetic target holdout、real target-point、public task-aligned benchmark 與 intervention validation。
- 將控制建議限制為 counterfactual action ranking。

## 已保留但重新標記的既有結果

- Synthetic 8-scenario field MAE：保留為 controlled synthetic full-field evidence。
- Hybrid residual leave-one-scenario-out：保留為 synthetic / controlled robustness evidence。
- 7-day real-bedroom pillow snapshot：改標記為 pillow target-point evidence，不再外推為 complete real 3-D field validation。
- SML2010 / CU-BEMS：保留為 public task-aligned benchmark，不作 dense spatial ground truth。

## 尚未完成同步

以下項目尚未完成，因此不應宣稱全部 thesis artifacts 已完全一致：

- 中文 Markdown 主稿同步。
- IEEE 英文稿 `docs/papers/ieee/paper.tex` 同步。
- PPT 與 speaker notes 同步。
- claim-to-evidence matrix 建立。
- 真實 bedroom_01 node deployment map。
- real target-point validation 的新資料圖表。
- output JSON、figures、LaTeX 數值一致性檢查。
- XeLaTeX 實際編譯確認。

## 使用注意

目前 LaTeX 已是 OpenSpec-aligned draft，但屬於研究主張與章節架構同步，不代表所有實驗輸出與圖表已重新產生。後續應先完成 claim-to-evidence matrix，再同步 IEEE 稿與簡報。
