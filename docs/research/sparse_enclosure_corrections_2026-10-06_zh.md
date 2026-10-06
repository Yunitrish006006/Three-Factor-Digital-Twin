# 稀疏機箱原型：獨立審查修正與接續入口

本次修正對應 [原獨立審查](../reviews/independent_research_review_2026-10-06_zh.md) 的三项 P2 問題，先提交 [修正 protocol](../../openspec/changes/correct-sparse-enclosure-review-20261006/protocol.md)，再實作；不是重新執行或改寫原凍結研究。

## 後續實作入口

新的控制研究請從 `digital_twin.control.sparse_enclosure_v2.TransferController` 匯入，呼叫：

```python
command, info = controller.step(
    estimated_state, inlet_temperature, declared_power, previous_pwm,
    observed_plate_air=raw_plate_air,  # 原始金屬片、空氣兩個觀測；必填
)
```

警告取「估測熱源」或「原始金屬片／空氣」任一越界，再經相同 PWM／變化率限制及 anti-windup。原始資料缺少或不合法就拒絕呼叫，不以濾波後觀測代替。熱源真值仍僅供 scorer 使用。歷史 `sparse_enclosure.py` 與原研究 runner 保留供凍結結果重現，不能視為新版控制入口。

結果完整性使用 `scripts/verify_sparse_enclosure_integrity.py`：除原計分核對，再查封存位元組、時間、真值連續性、輸入／噪聲來源、獨立熱平衡與風扇動態。新輸出一律保存於 `openspec/changes/correct-sparse-enclosure-review-20261006/artifacts/`。

## 本次結果與限制

- 原 108 回合、19,440 步通過新核對；獨立積分熱源差最大 0.000573905°C，低於事前 0.01°C 容差。
- 新版控制在已開啟的 72 回合、12,960 步輸入回放中，命令／警告差異為零。觀測器沿用封存動作；這是回歸檢查，沒有新閉迴路或未見確認證據。
- 接觸較差假設平台在入口 22°C、熱量 3.35W、全速風扇的熱源穩態為 32.40°C；六步 holdout 的 150/360 當下輸入若維持到穩態仍超過 30°C，實際取樣超溫是 124 步。穩態能力與有限時域軌跡不同，沒有改原判準或把所有超溫歸咎控制器。
- 同步腳本只讀取綁定檔案與證據 SHA256 的實際 QA 紀錄；內容改動會變成 STALE，缺紀錄是 NOT_EVALUATED，不會自动沿用歷史 PASS。
- 中文／IEEE／既有簡報已同步及重建；HTML 實際觀察三種寬度、導覽、展開及 Q/R 互動。PDF 僅檢查中文檔頁 89–90 與 IEEE 檔頁 7。完整 Office、HTML 列印、實體機箱驗證仍待完成；IEEE 仍為 8 頁。

## 驗證命令

```sh
.venv-mpc/bin/python -m unittest discover -s tests
.venv-mpc/bin/python scripts/verify_sparse_enclosure_integrity.py
.venv-mpc/bin/python scripts/replay_sparse_enclosure_v2.py
.venv-mpc/bin/python scripts/analyze_sparse_enclosure_capacity.py
.venv/bin/python scripts/verify_sparse_enclosure_sync.py
.venv/bin/python scripts/verify_thesis_results.py
.venv-mpc/bin/python scripts/validate_research_openspec.py
```

重建 HTML／PDF 後必須重新檢查改動範圍並另寫 hash-bound 觀察，不能只更新舊紀錄的雜湊。當新版動作真的改變時，要先建立新的閉迴路 protocol，不能把舊回放結果當成完整控制評估。

執行證據見 [corrective evidence](../../openspec/changes/correct-sparse-enclosure-review-20261006/evidence.md)；[獨立複審](../reviews/independent_research_rereview_2026-10-06_zh.md) 已確認三項問題解決，本次修正範圍未發現新的 P1／P2 缺陷。
