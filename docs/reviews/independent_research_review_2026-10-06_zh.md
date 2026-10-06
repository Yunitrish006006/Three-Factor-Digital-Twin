# 稀疏機箱原型與 LQR 備稿：獨立角色審查

日期：2026-10-06。受審版本：`2d0fe2f1ea33827e449d411d0cc1a25a80a75e48`。

使用者要求另一個角色審查。實際執行角色為 `independent_research_reviewer`，以全新上下文檢查 canonical `school/`；主代理另核對 LQR 原文與文件驗收紀錄，並重現警告判斷。這份記錄彙整已核實的發現，未修改研究程式、protocol、來源凍結或既有實驗結果。

## 判斷

現有成果可作為探索性研究進度與下週 LQR 介紹。沒有找到熱源真值直接送入估測／控制的路徑，原有 CSV 的指標核對與輸入限定重播均通過；報告也保留了六步排序未優於 PI、超溫及純合成的限制。

確認三項 P2 問題，應在下一輪驗證或沿用程式前修正。P2 表示會影響宣告行為或證據可信度的實質缺口；不代表已證實封存數字錯誤。本輪沒有確認 P0／P1。

## R1 — P2：過熱警告沒有依 protocol 檢查原始感測值

位置：[核心控制](../../digital_twin/control/sparse_enclosure.py) L159–184、[runner](../../scripts/run_sparse_enclosure.py) L99–106；[protocol](../../openspec/changes/prototype-sparse-enclosure-transfer-20261006/protocol.md) L19。

Protocol 指定「估測熱源，或實際觀測金屬片／空氣」超過 warning 時觸發 override。實作卻只檢查 `max(x[:3])`，其中金屬片／空氣也是 observer 的 posterior，controller 沒收到原始觀測。濾波可能把已超過門檻的感測值壓回門檻下，因而漏掉計畫中的警告。

已重現：observer 從 22°C 起始，以 PWM .4、零功率 predict 一步，輸入 plate=29.51°C、air=22°C、fan=.4。Posterior plate=29.4254°C、source=24.2817°C；`rank_h6` 的 `warning=False`，PWM 降為 .3。依 protocol 應 request=1，再依共同 slew 得 PWM=.5。

可重現片段（只呼叫函式，不執行 study runner）：

```python
from digital_twin.control.sparse_enclosure import HeatNetwork, SparseObserver, TransferController
p = HeatNetwork()
observer = SparseObserver(p, 22.)
observer.predict(.4, 22., 0.)
x = observer.update([29.51, 22., .4])
print(x, TransferController('rank_h6', p).step(x, 22., 0., .4))
```

獨立角色掃過既有 72 個 closed-loop 回合：原始觀測與 posterior 的警告判斷差異為 **0 步**。因此此缺口目前沒有改變已存結果，但會影響日後接上感測或新的熱動態時的行為。

修正方向：將原始 plate／air 觀測明確送入共同警告層，用原始感測值與估測熱源分別判斷，再套用共同命令限制。增加能區分「raw 超門檻、posterior 未超門檻」的回歸檢查；不要只測最終 PWM 是否在合法範圍。這仍不構成硬體安全保證。

## R2 — P2：結果驗證器漏查時間與 simulator-side 真值連續性

位置：[verifier](../../scripts/verify_sparse_enclosure.py) L46–73、[輸入重播](../../scripts/audit_sparse_enclosure.py) L30–41。

Verifier 檢查 `step=0..179` 與 PWM 連續性，但不檢查 `time_s=step×dt`、`source_truth_next[k]=source_truth_current[k+1]` 或 plant-side dynamics。輸入限定重播刻意不讀真值，不能補上這些評分資料的檢查。重新計算 CSV 指標只證明算式與 CSV 一致。

獨立角色在 `/private/tmp` 的資料副本實際做了兩個負向 probe，原 repo 完全未修改：

1. 把第一份 CSV 所有 `time_s` 改為 `123456`：`check_artifacts()` 與 `audit()` 仍回傳 `passed=True`。
2. 把第一份 CSV 的 `source_truth_next` 整欄逆序，僅重新計算該回合指標及對應宏平均，不改 frozen sources／config／calibration：兩個函式仍回傳 `passed=True`。

第二種輸入已不符合 runner 的狀態延續，卻能通過兩層驗證。這是評分資料驗證的盲點，沒有證實原有真值曾遭錯置；獨立角色另查現存全部 CSV，`source_truth_next[k]−source_truth_current[k+1]` 最大絕對差為 **0**。

修正方向：增加時間戳、初始狀態、熱源／風扇真值連續性與 simulator-side dynamics 核對，並保留上述負向 probe 作回歸檢查。演算法輸入稽核與評分真值稽核應分開。增加封存 evaluation trace 雜湊可協助察覺後續改動，但不能替代物理／時間一致性驗證。

## R3 — P2：同步檢查會把舊視覺 QA 綁到新的 HTML 雜湊

位置：[同步檢查腳本](../../scripts/verify_sparse_enclosure_sync.py) L75–88。

`observed_qa` 是硬編碼敘述。每次執行都會更新目前 HTML 的 SHA-256，同時重寫「1440／820／390、錨點／互動正常、無 console error」的舊紀錄，而腳本沒有執行這些瀏覽器檢查，也不要求舊 QA 對應同一份 HTML。

主代理已在 `/private/tmp` 建立臨時 root：其他需要的來源與成品使用唯讀 symlink 指向原 repo，唯獨 HTML 改成含 `href="#missing"` 與 `throw new Error("broken QA")` 的頁面；再把函式的 `ROOT`／`ARTIFACTS` 指向此 root。

結果：仍顯示 **PASS: 18 synchronization checks**，新的 manifest 仍宣稱原有視覺 QA。這不表示前一輪實際瀏覽檢查沒做；它表示重跑此腳本會替日後不同內容錯誤延用驗收。

修正方向：將「這次自動內容核對」與「當時實際觀察」分成不同記錄。視覺 QA 應含實際受驗 HTML 雜湊、日期與檢查證據；目前 HTML 改變時標示 `STALE`／`NOT_EVALUATED`，只有重新觀察後才更新。腳本不應自行產生新的視覺驗收敘述。

## 研究解釋待補：先區分散熱能力與控制器誤差

這是後續研究分析，未列為已證實程式 bug。現有模型有一部分負載即使風扇全速，長期穩態也無法低於 30°C。若只看 tracking／超溫，可能把散熱能力不足全部歸因於控制器。

獨立角色與主代理分別用凍結係數解三節點穩態線性方程：`contact_poor`、fan=1、入口 22°C、總熱量 3.35W（含模擬中的 .15W 未觀測熱量）時，熱源平衡點為 **32.3999°C**。在該平台 H6 holdout 的 360 步輸入中，150 步的「若將當下輸入維持到穩態」全速平衡點高於 30°C。

這不代表已有 150 步發生超溫，也不直接判定有限時域不可行；實際溫度還受初始狀態、熱容量及後續負載影響。它不使共同限制下的比較不公平，但顯示需要加入可達平衡點與散熱能力分析，再解釋哪些誤差／超溫能靠控制改善，哪些需要改善接觸、散熱片、風量或降低熱負載。

此計算僅讀取既有 config 與 CSV，未重跑實驗；是審查診斷，未追補為原 study 的事前成功判準。

## 已確認與尚未完成的範圍

- 審查者唯讀呼叫 `check_artifacts(ARTIFACTS)` 與 `audit()`：108 回合／19,440 步 PASS，calibration fallback=0；沒有重跑 frozen study 或 E15。
- LQR 選文、原文 p.104 的精確狀態假設，以及 p.114 的附條件穩定定理可核對。[Kalman 原文](https://boletin.math.org.mx/pdf/2/5/BSMM%282%29.5.102-119.pdf)支持這些介紹；未逐行重證全部論文證明。
- HTML 的一維 Q／R 示意與其 caption 的 `A=-.01` 相符；程式 `a=.01` 是正的衰減係數，`sqrt(...)-a` 對該例正確。沒有把這一記號差異列為錯誤。現代 ARE 可另核對 [SciPy 官方定義](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_continuous_are.html)。
- 純合成、單一方程家族、已知容量／部分係數、僅兩個 holdout seeds、沒有實機與完整三因子遷移，文件已明確揭露；屬後續研究缺口，未當成隱藏錯誤。
- 完整 Office 視覺 QA 尚未完成，IEEE 稿目前 8 頁而既定目標 6–7 頁，已在同步紀錄中列待辦。本次未做新的瀏覽器或 Office 逐頁驗收。
- 10/5 舊對照只為理解本輪引用與資料契約而查閱；本審查未重新全面審查所有歷史 thesis experiments，也未重跑先前 314 項單元測試。

## 處理順序

先修 R1 的警告資料契約，再補 R2 的評分資料驗證，最後將 R3 視覺 QA 拆成有內容雜湊的觀察紀錄。R1 涉及已凍結算法：應使用明確的新版本／研究 change，保留原來源與結果；不能把修正後結果覆蓋既有研究。R2／R3 可增加獨立審查工具，但亦須避免改動 frozen verifier 而不留偏差紀錄。

上述修正本次均未實作。這份審查的完成不等於問題已修復，也不等於現有原型已可實機部署。
