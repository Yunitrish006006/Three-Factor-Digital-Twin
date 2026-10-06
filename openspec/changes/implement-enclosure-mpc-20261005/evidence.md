# Evidence

執行日期 2026-10-05。第一階段範圍為假設機箱模型的探索性模擬；未採納為主論文確認成果。實體機箱、NTC、throttling、整機功耗與 E8 為 NOT_EVALUATED，LQR 為 TODO。

## 實際執行

1. 先建立計劃、research-first protocol、method/source record，再實作。
2. 專用 Python 3.11.15／NumPy 1.26.4／SciPy 1.14.1。原 `.venv` 因 Xcode license 無法啟動，另建立 `.venv-mpc`，沒有修改其原設定。
3. 完成熱能平衡、fan lag、affine prediction、bounded command、MPC/PID/fixed 與求解驗證；12 項針對性測試通過。
4. 共 25 候選、75 calibration episodes；僅依 calibration 選出 fixed PWM=0.4、PID Kp=0.06/Ki=0.0001/Kd=0.05、MPC R_u=1。凍結來源與結果才進入正式 evaluation。
5. 36 正式 episodes、4,320 個控制步，三方法各自完成 validation/holdout/mismatch/overload ×3 seeds；各20 min。保留全部 CSV、JSON、hash、slack、safety override 與 failure reason。
6. verifier 通過所有 36 個 trace/source/freeze hashes、原始指標重算、同擾動 parity、PWM/slew 與 fallback 規則。
7. 完整 repository 測試：286 tests，初次27.812 s、最終27.751 s，兩次均OK。log 內 E15 runner 輸出是單元測試的隔離 fixture／mock；沒有重跑 canonical E15 實驗。
8. OpenSpec validator 通過：14 spec files，130 requirements，251 scenarios，32 active changes。先前 systematic-parameter-tuning change 的 design/delta specs 缺漏依既有證據補齊，沒有新增研究數值。

## 結果

各列是三 seed 的 macro mean，不是實體樣本統計。

| Split | 方法 | tracking MAE °C | overtemp s | fan proxy Wh | fallback 步／回合 |
| --- | --- | ---: | ---: | ---: | ---: |
| validation | fixed | 3.5279 | 0 | 0.2133 | 0 |
| validation | PID | 2.4592 | 0 | 0.4744 | 0 |
| validation | MPC | 1.2500 | 0 | 0.7015 | 0 |
| holdout | fixed | 5.4378 | 0 | 0.2133 | 0 |
| holdout | PID | 2.6034 | 0 | 0.5873 | 0 |
| holdout | MPC | 1.4426 | 0 | 0.8234 | 0 |
| mismatch | fixed | 8.8199 | 0 | 0.5848 | 0 |
| mismatch | PID | 3.7977 | 0 | 1.5133 | 0 |
| mismatch | MPC | 3.5426 | 0 | 1.4306 | 0 |
| overload | fixed | 27.7470 | 1116.7 | 3.0572 | 0 |
| overload | PID | 26.3322 | 1046.7 | 3.2470 | 0 |
| overload | MPC | 26.1913 | 1040.0 | 3.2722 | 63.33 |

- H-MPC-01：SUPPORTED_SIMULATION_ONLY；六個 nominal MPC episodes 無 PWM/slew 違例、無 solver fallback，p95 求解時間低於10 s。此 gate 不涉及硬體安全。
- H-MPC-02：SUPPORTED_SIMULATION_ONLY；holdout macro MAE 相對本輪 PID 降低44.587%，且各 seed 超溫時間無增加。但 fan energy proxy 提高40.20%，PWM variation 增加；不能宣稱整體優越或節能。
- CLM-MPC-SIM：僅支持固定假設模型、固定 baseline 預算下的探索性結果。不同候選數、名義參數共享、完整状态可见及僅三 seed 都是限制。
- 模型失配的 MPC RMSE 4.5002°C 略高於 PID 4.4851°C，負向結果保留。
- 過載最大風扇也無法避免超溫；MPC 190/360 步回退，溫度限制以 soft slack 表示，並非硬性安全保證。下一版若改求解器／縮放需另立版本，不覆寫本結果。

## 產物與同步

- [freeze](artifacts/freeze.json)、[calibration](artifacts/calibration.json)、[result](artifacts/result.json)、[verification](artifacts/verification.json)。
- [MPC 方法](../../../docs/research/enclosure_mpc_method_2026-10-05_zh.md)、[計劃表](../../../docs/research/mpc_execution_plan_2026-10-05_zh.md)、[HTML](../../../docs/reports/enclosure_mpc_2026-10-05_zh.html)。
- 中文 thesis/build source、IEEE/reference、既有 presentation source/outlines 已納入相同 exploratory 補充。DOCX、中文 PDF、IEEE PDF 與兩套既有 PPTX 已由原 builders 重建；IEEE 最終為7頁，已檢視新增段落與參考文獻版面。見 [輸出核對](artifacts/artifact_sync_verification.json)。
- 新增科学圖獨立於室內主架構圖；主架構未改，因此沒有重建無關圖。
- PDF 已檢視新增段落頁面；HTML 桌面／平板／手機、錨點、展開、局部表格捲動與 console 已檢查。完整 DOCX／PPTX 逐頁視覺 QA 尚未完成：本回合沒有可用的 bundled LibreOffice/runtime dependency loader。已重建與內容核對，不宣稱完整排版審核通過。
- 保留開工前已有的9/21 HTML、講稿與未追蹤待辦修改；沒有 commit、push 或外部發布。

## 偏差與仍需工作

SciPy 在部分迭代提出 bounds clipping warning，最終命令仍另檢查。過載求解失敗完整記錄且不重調。兩個同 synthetic fixture 的重跑僅是 repeatability audit，不是新增 holdout。沒有研究結果驅動的門檻或模型修改。額外 closure audit 已核對75 calibration episodes與選參規則，重現 nominal/stress 同 fixture 的 numerical hashes，並重算 H-MPC-02；見 [closure audit](artifacts/closure_audit.json)。

MPC 第一階段核心實作／模擬完成。後續 LQR、四方法比較、獨立模型辨識、實機介入與完整 Office 輸出視覺 QA 各自保持未完成，不將軟限制或模擬通過升級為設備安全。
