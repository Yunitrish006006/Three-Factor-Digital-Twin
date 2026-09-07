# 研究難題與決策日誌

本日誌記錄研究執行中實際遇到的阻礙，不只記錄成功結果。每筆紀錄至少包含現象、原因、嘗試、處置、研究影響與狀態；不得把尚未解決的問題改寫成已完成。

## 2026-08-23：設備機箱公開資料基線

### RDL-001：初始資料沒有可評估案例

- 現象：最初抽取的 6 條 BMC trace 全部無法形成符合門檻的訓練與測試配對。
- 原因：20--30 °C 適用範圍、時間間隔與最小樣本數共同造成資料淘汰。
- 嘗試：沒有放寬溫度或取樣門檻，改為依原協定擴大至資料庫全部 124 個 CSV。
- 處置：保留門檻並完整報告排除原因。
- 研究影響：317 個裝置檔案案例中僅 5 個可評估，外部效度受到明確限制。
- 狀態：已處置，但資料稀疏問題仍存在。

### RDL-002：物理基線未優於 persistence

- 現象：thermal-balance baseline 在 5 個合格案例中皆未取得最低測試 MAE；persistence 為 5/5。
- 原因：目前資料與模型不足以辨識穩定的熱平衡參數，且合格案例少、時間跨度有限。
- 嘗試：同時比較 persistence、線性迴歸與 thermal-balance，並保留逐案例結果。
- 處置：將 H-ENC-01 判定為不受支持，不調整門檻追求正結果。
- 研究影響：E11A 只能作為負向可行性證據，不能支持機箱空間數位分身的有效性主張。
- 狀態：研究決策已完成；E11B 需改用含 3D 幾何與風場的資料。

### RDL-003：命令列腳本無法從儲存庫根目錄匯入套件

- 現象：直接執行 `scripts/run_enclosure_bmc_baseline.py` 時找不到 `digital_twin`。
- 原因：Python 的模組搜尋路徑以 `scripts/` 為起點，沒有包含儲存庫根目錄。
- 嘗試：確認失敗位置後，在腳本啟動時加入根目錄路徑。
- 處置：修正 CLI 匯入路徑並以 3 個針對性測試覆蓋基線行為。
- 研究影響：不影響數值結果，但原始命令缺乏可重現性。
- 狀態：已解決。

### RDL-004：文件建置依賴與系統環境不一致

- 現象：系統缺少 `python-pptx` 與 `tectonic`，且 Tectonic 預設快取位於唯讀家目錄。
- 原因：`pyproject.toml` 未宣告文件建置依賴；README 所述 Homebrew 安裝不適用目前環境。
- 嘗試：先使用現有環境，失敗後將 Python 套件、Tectonic 執行檔與快取限定於 `/tmp`。
- 處置：完成 DOCX、PDF、PPTX 與 IEEE PDF 重建，沒有將臨時工具寫入儲存庫。
- 研究影響：研究內容不受影響，但重建流程尚未完全自包含。
- 狀態：本次已繞過；依賴宣告仍待改善。

### RDL-005：中文 PDF 硬性依賴特定商用字型

- 現象：Tectonic 因找不到 `Times New Roman` 中止，後續亦可能缺少 Arial、Menlo、Songti TC 與 Heiti TC。
- 原因：建置腳本沒有跨平台字型 fallback。
- 嘗試：盤點系統字型並確認 Liberation 與 Noto CJK 系列可用。
- 處置：保留原字型優先順序，缺少時改用 Liberation Serif/Sans/Mono 與 Noto Serif/Sans CJK TC。
- 研究影響：正文與研究結論不變；不同機器的字型度量可能造成少量分頁差異。
- 狀態：已解決，仍需在提交機器上檢查最終版面。

## 後續記錄規則

- 每次實驗、資料處理、建模、同步或建置遇到非預期問題時新增一筆 `RDL` 紀錄。
- 實驗失敗、null result、資料缺失與不利結果必須保留。
- 暫時 workaround 與根本修正必須分開標示。
- 若問題改變方法、門檻、指標或結論，必須同步更新 OpenSpec、論文與簡報。

## 2026-08-23：AAU 伺服器機房 E11B 前置調查

### RDL-006：官方網頁無法預覽主要資料與配置表

- 現象：Zenodo 無法預覽 706.2 MB 溫度 CSV，XLSX 下載連結在文字擷取工具中發生 Unicode decoding error。
- 原因：檔案格式與容量超出網頁預覽能力，研究環境亦未安裝 XLSX 讀取工具。
- 嘗試：先讀 REST metadata，再將 `openpyxl` 暫時安裝於 `/tmp`，只檢查配置表欄位。
- 處置：確認配置表有 6 個 rack、75 列設備配置，但沒有感測器座標。
- 研究影響：不能只依配置表建立空間資料，必須交叉解析 CAD log 與官方標註圖。
- 狀態：已繞過；原始資料可讀性仍不理想。

### RDL-007：座標、channel 名稱與語意分散在不同檔案

- 現象：CSV 僅提供 `Temperature mod N ch N`；CAD log 只有 PT100/Anemometer 座標；channel 語意則畫在 JPG 標註圖中。
- 原因：資料集缺少單一 machine-readable channel-to-coordinate manifest。
- 嘗試：交叉核對 3D 標註圖、平面圖與 AutoCAD `LIST` log。
- 處置：先建立 42 個高信心溫度點；暫時排除左右方向可能互換的 6 個冷卻設備點。
- 研究影響：E11B 第一階段只評估高信心點，不能把 48 個 channel 全部宣稱為已可靠定位。
- 狀態：部分解決；6 個冷卻點映射待獨立確認。

### RDL-008：主檔過大且每秒有重複 timestamp

- 現象：溫度／功率 CSV 為 706,160,545 bytes；64 KiB 樣本中同一秒可出現多筆讀值。
- 原因：高頻量測輸出只保留秒級 timestamp，完整下載與逐列處理成本高。
- 嘗試：確認 Zenodo 支援 HTTP Range，並先讀取 64 KiB schema 樣本。
- 處置：預註冊 12 個等距 4 MiB byte-range，丟棄片段首尾不完整列，再做每分鐘 median 聚合。
- 研究影響：結果代表跨檔案範圍的決定性分層樣本，不等同完整 706 MB 全量分析。
- 狀態：協定已執行；12 個固定 range 產生 97,735 筆合格列與 1,641 個一分鐘快照，仍不等同完整檔案分析。

### RDL-009：資料集頁面缺少明確 license 欄位

- 現象：Zenodo 頁面標示 Open，但 REST metadata 的 `rights` 與 `access` 為 null。
- 原因：資料紀錄未提供可機器判讀的再散布授權。
- 嘗試：檢查網頁 Rights 區塊與 REST metadata，皆未取得具體授權名稱。
- 處置：原始檔只存於 `/tmp`，儲存庫只保存自行產生的座標 manifest、程式、指標與來源引用，不再散布原始檔。
- 研究影響：不影響本地可重現分析，但限制原始資料打包與鏡像。
- 狀態：授權不確定性仍存在。

### RDL-010：房間格式文件與驗證器規則不一致

- 現象：格式文件允許在 `metadata.reason` 說明非標準感測器配置，但 `validate_room_design.py` 仍強制要求 8 個標準角落感測器。
- 原因：文件需求已容許研究型配置，驗證器尚未實作同一例外規則。
- 嘗試：不修改既有 validator，避免本次研究順便放寬全專案格式契約。
- 處置：AAU room design 同時提供 8 個 schema anchor 與 42 個真實 PT100；評估器只讀有 `metadata.csv_column` 的量測點。
- 研究影響：room design 的 `sensors` 數量為 50，但 E11B 的實驗感測器數仍嚴格為 42。
- 狀態：本次可驗證；文件與 validator 的根本差異待獨立修正。

### RDL-011：預註冊資料下載未獲執行授權

- 現象：執行 `python3 scripts/download_aau_temperature_ranges.py` 的外部網路權限請求被拒絕，12 個正式 range 尚未下載。
- 原因：終端機外部網路執行需要額外核准；本次核准沒有取得。
- 嘗試：僅提出一次依預註冊協定的 48 MiB 下載請求，未改用其他工具繞過授權。
- 處置：第一次拒絕後停止正式執行；使用者後續明確允許下載，才依原協定執行同一組 12 個 range，未改變 offset。
- 研究影響：授權等待延後 E11B，但沒有以 64 KiB schema 樣本取代正式指標。
- 狀態：已解除；下載與正式評估完成。

### RDL-012：全域 3D IDW 不如最近鄰，且不能在看過結果後調參

- 現象：最近鄰 MAE 為 1.175 °C，明顯優於 3D IDW 的 1.687 °C；最近鄰在 30/42 個感測器勝出，IDW 僅 6/42。
- 研究難點：幾何距離較完整不代表預測較準確。機櫃阻隔、送回風方向與垂直熱分層可能使全域、等向性距離權重混入不相似位置，但本實驗無法辨識真正原因。
- 處置：依預註冊規則將 H-ENC-02 判定為不支持，不在看過結果後調整 `p` 值、感測器座標或排除規則。
- 報告方式：保留負向結果，區分「觀測到最近鄰較佳」與「可能原因」；後續若測試機櫃拓撲或非等向性模型，必須建立新的 OpenSpec 變更與假說。
- 狀態：研究決策已完成；可能原因仍待獨立實驗。

### RDL-013：論文 PDF 可生成，但字型可攜性與表格行寬仍有警告

- 現象：中文 PDF 建置成功，但 Tectonic 回報系統字型絕對路徑不可完全重現，E11B 附近表格最大 overfull 約 21.107 pt；`build_thesis_pdf.py` 另有既存 invalid escape sequence 警告。IEEE PDF 也有最大 1.5117 pt 的輕微 overfull。
- 原因：中文排版依賴主機字型 fallback，長欄位與固定頁寬的組合超出部分 LaTeX box；Python docstring 中的反斜線未使用 raw string。
- 處置：本輪保留成功產出的 PDF 與完整 warning，不在研究結果同步階段順便改寫排版引擎。
- 研究影響：不影響 E11B 數值與假說決策，但跨機器像素級重建與表格視覺品質仍需獨立修正。
- 狀態：開放中的文件工程技術債。

### RDL-014：新增結果檢查器誤判 JSON 層級，且 canonical registry 殘留舊狀態

- 現象：第一次執行 `verify_e11b_results.py` 發生 `KeyError: metrics`；stale-text search 同時找到 E11B 仍為 `NOT_EVALUATED` 的舊 registry 行。
- 原因：檢查器依照摘要名稱假設頂層 schema，未使用實際 `evaluation.macro_metrics`、`evaluation.sensor_wins` 與 `evaluation.hypothesis` 路徑；同步補丁也只更新 EVD-019，漏掉 EVD-002 registry scenario。
- 處置：依 committed JSON 契約修正檢查器，並把 registry 更新為 E11A/E11B 都是 `REPRODUCIBLE` 的有界負向證據。
- 研究影響：沒有改動資料、模型或指標，只修正驗證邏輯與狀態一致性；第一次驗證不得計為通過。
- 狀態：已解決；OpenSpec、E11B consistency 與 stale-text search 重跑通過。

### RDL-015：下載器沒有 `--help`，查詢介面反而重寫 E11B manifest

- 現象：執行 `python3 scripts/download_aau_temperature_ranges.py --help` 時，腳本忽略參數並重新進入下載流程；12 個既有 fragment 均以 exact-size reuse，manifest 的 `generated_at` 與 `retrieval` 被改寫。
- 原因：E11B 下載器沒有 argparse 入口，也沒有拒絕未知參數。
- 資料完整性：12 個 offset、檔案大小與 fragment SHA-256 均未改變；`aau_spatial_baseline.json` 亦未重算且 SHA-256 仍為 `9b0a98dc45d78c4ae8484a40f07d20fbff4950976944c81bb743cc98ad6966ee`。manifest SHA-256 由原 run 的 `788fae...` 改為 `592a08...`。
- 處置：依使用者決定保留新 manifest，不回復時間欄位；E11B evidence 同時保存原始 run hash 與目前 manifest hash。E11C 下載器改用 argparse，使 `--help` 無副作用且未知參數直接失敗。
- 研究影響：E11B 指標與原始片段內容不變，但 manifest 本身不再是原始 run 的 byte-for-byte artifact，報告時必須揭露。
- 狀態：已揭露並建立後續防呆。

### RDL-016：E11C delta spec 首次驗證缺少 level-1 標題

- 現象：下載前執行 `validate_research_openspec.py` 失敗，指出 delta spec 必須以 level-1 title 開始。
- 原因：檔案直接從 `## ADDED Requirements` 開始，符合內容語意但不符合儲存庫結構 validator。
- 處置：在 requirement 區塊前加入 `# E11C Evaluation and Evidence Delta`，不改研究問題、offset、模型或決策門檻。
- 研究影響：只影響規格可驗證性；confirmation data 尚未下載，因此沒有 post-hoc 研究變更。
- 狀態：已解決；OpenSpec 重跑通過。

### RDL-017：原 12 個互補 offsets 中有區段與 E11B 重疊

- 現象：E11C 下載器在網路請求前執行 overlap guard，於 offset `321734527` 立即失敗；另一原候選 `380231713` 亦會跨入 E11B 區段。
- 原因：原公式把 12 個中心點均勻放在整個可用 offset 範圍，沒有保證每點落在 E11B 區段之間的空隙；人工抽查未涵蓋中央區段。
- 處置：捨棄原 12 點公式，改以相鄰 E11B start offsets 的整數中點定義 11 個 gap-centered ranges，每個間隙一個；下載器仍以 interval guard 作機器檢查。
- 研究影響：失敗發生在任何 HTTP retrieval 與 confirmation metric 前，因此可修正預註冊的資料可行性，不構成看過結果後選樣；樣本量由約 48 MiB 改為約 44 MiB。
- 狀態：已解決；OpenSpec 通過，11 個 ranges 均通過 overlap guard 並完成 HTTP 206 retrieval。

### RDL-018：E11C 下載期間缺少即時進度輸出

- 現象：11 個 ranges 約兩分鐘下載期間，程序持續存活但終端沒有逐段訊息，完成時才一次輸出全部 range 狀態。
- 原因：非互動 Python stdout 採 block buffering，原 `print` 未指定 `flush=True`。
- 處置：下載成功後仍保留 manifest；後續版本的 range 與完成訊息改為即時 flush，不重跑資料來美化紀錄。
- 研究影響：不影響 bytes、hash 或 overlap 結果，但執行中難以區分正常下載與停滯。
- 狀態：已改善後續可觀測性。

### RDL-019：E11C runner 從 `scripts/` 執行時無法匯入專案套件

- 現象：第一次執行 `run_aau_local_idw_confirmation.py` 立即發生 `ModuleNotFoundError: No module named 'digital_twin'`。
- 原因：Python 將腳本目錄而非 repository root 放入 import path，runner 未沿用先前 RDL-003 的 CLI 啟動修正。
- 處置：在任何專案套件 import 前，將 `Path(__file__).resolve().parents[1]` 加入 `sys.path`；不改 confirmation data、模型或門檻。
- 研究影響：失敗發生在 manifest 讀取與 metric execution 前，沒有部分結果或 post-hoc 選擇。
- 狀態：已解決；runner 通過 import 並完成正式輸出。

### RDL-020：既有 AAU parser 把 byte-zero header 與 observation range 綁在一起

- 現象：修正 import 後，runner 在 metric 前以 `range zero must be the first manifest fragment` 中止。
- 原因：E11B parser 只從 start=0 fragment 讀 CSV header；E11C 為獨立確認刻意排除所有 E11B ranges，因此沒有 byte-zero fragment。
- 處置：manifest 新增固定 `csv_header` schema，parser 可用它解析非零 ranges；byte-zero header 只提供欄名，不讀取任何 byte-zero observation row。另加測試確認非零 fragment 可獨立解析。
- 研究影響：保留 E11C observation 與 E11B discovery rows 的資料分離；只共用公開檔案的欄位 schema。
- 狀態：已解決；新增測試通過，E11C 僅以固定 header schema 解析 11 個非零 ranges。

### RDL-021：local IDW 整體誤差改善，但只覆蓋一半感測器

- 現象：local IDW 將 macro MAE 從 1.301 降至 1.223 °C、RMSE 從 2.218 降至 1.886 °C，day-block-bootstrap 95% CI [0.0546, 0.1063] °C 全為正；但 per-sensor 僅 21/42 勝出，未達 26/42 門檻。
- 研究難點：aggregate improvement 與 sensor-wise coverage 指向不同結論。少數大幅改善點可能拉低整體 MAE，但不能代表方法普遍適合各感測器角色。
- 處置：依四項預註冊條件將 H-ENC-03 判定為不支持，不因通過其中三項就改成支持或降低 60% 門檻。
- Exploratory 診斷：local IDW 在 gradient 0/5、rack back 17/28、rack front 4/9 勝出；此異質性只能用於形成新假說，不能證明氣流或機櫃拓撲原因。
- 後續原則：若研究 sensor-role-aware 或 topology-aware 方法，須使用新的資料切分與 OpenSpec，不得回頭用 E11C confirmation metrics 選規則。
- 狀態：正式決策完成，後續機制假說尚未驗證。

### RDL-022：final shell check 的 regex 與 PDF 工具假設不成立

- 現象：stale-text pattern 把 `not supported／不支持` 誤匹配為 `supported／支持`；同一命令又因環境沒有 `pdfinfo` 而 exit 1。
- 原因：負向詞包含正向詞子字串，且驗證腳本假設 Poppler 工具存在。
- 處置：舊狀態搜尋只保留 `NOT_EVALUATED`、尚未評估、仍待驗證等真正 stale tokens；頁數改從 Tectonic log 的 `Output written ... (N pages)` 取得。
- 研究影響：其他 consistency validators 均已通過；這是 validation harness 的假陽性與環境依賴，不是 E11C 數值錯誤。
- 狀態：已解決；真正 stale tokens 搜尋為空，頁數由 Tectonic log 成功取得。

### RDL-023：加入 E11C 後 IEEE 稿增至 8 頁

- 現象：`paper.log` 顯示 `Output written on paper.xdv (8 pages, ...)`，超過 IoTaIS full paper 的 6–7 頁目標。
- 原因：E11B 與 E11C 各自使用長 subsection，並重複資料邊界、方法與失敗解讀；新增引用也增加 bibliography 長度。
- 處置：因 enclosure transfer 不是 headline novelty，IEEE 稿將 E11B/E11C 壓成單一 bounded transfer 段落，保留樣本數、MAE、wins、CI 與負向決策，移除 exploratory 分群與重複敘述。中文論文與教授報告仍保留完整細節。
- 研究影響：不改任何實驗結論，只調整投稿稿件資訊密度；若仍超過 7 頁，需進一步刪減次要服務層內容。
- 狀態：已解決；第二次內容壓縮後 Tectonic log 顯示 7 pages，E11B/E11C consistency verifiers 仍通過。
## RDL-024：外部資料下載受沙箱 DNS 限制

- **階段**：E11D 配置資料準備。
- **難題**：在預設沙箱執行 `curl` 時無法解析 `zenodo.org`，第一次下載在寫入任何有效檔案前失敗。
- **處理**：依授權流程改以已核准的網路權限重跑，只下載 AAU v4 的 24.5 kB 官方配置檔，並保留官方 DOI 與 URL。
- **研究影響**：沒有接觸 E11D 觀測區段，也沒有改變預註冊模型或門檻；屬執行環境限制。
- **狀態**：已解決。

## RDL-025：本機缺少 XLSX 解析套件

- **階段**：E11D 配置資料準備。
- **難題**：配置檔下載成功後，Python 環境沒有 `openpyxl`，原定的唯讀檢查失敗。
- **處理**：不安裝新依賴，改用 Python 標準函式庫 `zipfile` 與 `xml.etree.ElementTree` 解析 OOXML。檢查發現工作簿是機櫃設備清單，不是感測器座標表，因此未把它錯當成角色座標證據。
- **研究影響**：促使 E11D 使用已凍結且具雜湊的 E11C 角色中介資料；配置清單只作來源查核，不參與結果估計。
- **狀態**：已解決。
## RDL-026：E11D delta spec 缺少機器可驗證的需求編號

- **階段**：E11D 預註冊驗證。
- **難題**：初稿雖使用 `Requirement` 標題，卻沒有 `EVD-nnn` 識別碼，`validate_research_openspec.py` 因而判定沒有有效需求。
- **處理**：在任何 E11D 觀測資料下載前，將需求固定為 `EVD-022`；研究問題、模型、切分與門檻均未改動。
- **研究影響**：無結果資訊外洩，預註冊閘門保持有效。
- **狀態**：已解決。
## RDL-027：預註冊 Python 下載器的網路執行權限未獲核准

- **階段**：E11D 觀測區段下載。
- **難題**：OpenSpec 通過後執行 `urllib` 下載器時，執行層拒絕該命令的外部網路權限；沒有任何 fragment 因此命令而產生。
- **處理**：使用先前已核准的 `curl -fL` 能力，對完全相同的固定 ranges 發送請求；下載器新增 `--from-existing-curl`，以正式程式驗證最終 HTTP 206、精確 byte count、Content-Range 與 SHA-256，再產生 manifest。
- **研究影響**：傳輸工具改變，但資料 URL、offset、長度、邊界規則、模型及決策門檻均未改變。
- **狀態**：已解決。
## RDL-028：凍結角色資訊是由感測器鍵名隱式編碼

- **階段**：E11D 分析啟動。
- **難題**：E11C 結果沒有獨立的 `role` 欄位；角色位於 `gradient_1`、`rack_1_front`、`rack_1_back_1` 等 `per_sensor` 鍵名，而真正 CSV 欄位另存於 `csv_column`，初版 resolver 因此取得 0/42 筆並在讀取 E11D 溫度值前中止。
- **處理**：只檢查 E11C 結構鍵與 E11D CSV header，不查看 E11D 結果；resolver 改成由凍結鍵名推導三種已預註冊角色，再對應其 `csv_column`。新增相容性單元測試。
- **研究影響**：修正資料介面，不改變角色分組、模型、樣本、指標或決策門檻。
- **狀態**：已解決。
## RDL-029：正向整體結果仍不能直接解釋為氣流因果

- **階段**：E11D 結果判讀。
- **難題**：角色條件模型的 MAE 由 2.3972 降至 1.6517 C，且 30/42 感測器勝出，容易被過度表述為已證明冷／熱通道氣流機制。
- **處理**：只接受預註冊的預測性結論：固定角色語意相較全域平均具有可轉移資訊。保留 global mean 是簡單 baseline、E11C 與 E11D split 不同、沒有風速或干預資料等限制。
- **研究影響**：H-ENC-04 為 `supported`，但不宣稱因果、不把 E11D 用於事後調參，也不取代論文的 IoT 稀疏感測主軸。
- **狀態**：持續限制（論文與報告中保留）。
## RDL-030：最小單元測試漏建第三種預註冊角色

- **階段**：E11D 完整測試。
- **難題**：新增測試只建立 rack-front 與 rack-back fixture，但評估輸出固定彙整 gradient，造成空集合除以零；完整套件 184 項中有 1 項錯誤。
- **處理**：依使用者同意，只在測試 fixture 補入兩個 gradient 感測器，並把預期勝出數由 4 改為 6；生產演算法、E11D 原始資料與結果 JSON 均不變。
- **研究影響**：屬測試資料完整性問題，不影響 H-ENC-04 的 supported 決策。
- **狀態**：已解決。
## RDL-031：NTC 的精度不能只由標稱阻值判定

- **階段**：機箱實測硬體可行性評估。
- **難題**：市售 NTC 常只標示「10 kOhm、B3950」，但研究精度同時受 R25/B 容差、封裝耗散、自熱、ADC 參考、分壓電阻、導線與安裝位置影響；把元件精度直接當系統精度會低估誤差。
- **處理**：限定採用可追溯料號與原廠 R-T 表，採 ratiometric 讀取、逐通道校正及獨立確認；NTC 作低成本待測感測器，TMP117 或校正 PT100 作共址參考。
- **研究影響**：目前只形成硬體可行性與候選規格，尚未改變論文方法或宣稱新的實測結果。
- **狀態**：待正式 OpenSpec 與硬體實驗解決。
## RDL-032：三角色測試 fixture 意外形成數學上的全域平均 tie

- **階段**：E11D 測試修正確認。
- **難題**：首次補入 gradient 時設為 25 C，剛好等於 20 C front 與 30 C back 的平均，使其中一群的 global baseline 誤差為零，預期 6 次角色勝出但實際只有 4 次。
- **處理**：將純合成的 gradient fixture 改為非對稱 50 C，確保測試目的是真正驗證三群 role-conditioned prediction；不改生產演算法或 E11D 資料。
- **研究影響**：只影響測試設計，亦說明合成 fixture 需避免未註明的代數退化情形。
- **狀態**：已解決。

## RDL-033：DOCX 建置器依賴 macOS 專用 SVG 工具與暫存路徑

- **階段**：E11D 同步產出重建。
- **難題**：Linux 環境沒有 `qlmanage`，且原程式把暫存目錄固定為 `/private/tmp`，因此在文件內容處理前中止。
- **處理**：保留 macOS 路徑，並加入 ImageMagick `convert` fallback；暫存位置改用 `tempfile.gettempdir()`。
- **研究影響**：只改善文件工程可攜性，不變更圖、文字、指標或結論。
- **狀態**：已解決。
## RDL-034：E11D DOCX 後處理錯誤引入未安裝依賴

- **階段**：E11D 中文論文重建。
- **難題**：原建置器能以標準函式庫產生 DOCX，但新增的 E11D 後處理誤用未安裝的 `python-docx`；主 DOCX 已寫出後，程序在同步副本前失敗。
- **處理**：移除新增依賴，改以 `zipfile` 與 OOXML 標準函式庫插入 E11D 段落，並由同一建置器同步重建後的 Markdown 與 outputs 副本。
- **研究影響**：文件介面修正，不改研究結果；失敗產出不視為完成版本。
- **狀態**：已解決。
## RDL-035：論文建置工具與 TeX bundle 位於非預設暫存路徑

- **階段**：E11D 同步產出重建。
- **難題**：預設 shell 找不到 `tectonic` 與 `python-pptx`；找到編譯器後，新建的唯讀／空 cache 又無法取得網路 bundle。
- **處理**：重用前次已存在的 `/tmp/school-bin/tectonic`、`/tmp/tectonic-cache` 與 `/tmp/school-pydeps`，分別透過 `PATH`、`XDG_CACHE_HOME` 與 `PYTHONPATH` 明確指定，未下載或更換相依版本。
- **研究影響**：產出可在本次環境重建，但 `/tmp` 依賴不是長期可攜方案；應後續固定正式 build environment。
- **狀態**：本輪已解決，長期可攜性待改善。
## RDL-036：產生器重寫來源使手動同步文字消失

- **階段**：E11D 最終同步驗證。
- **難題**：IEEE 插入規則沒有匹配 `Discussion and Conclusion` 章名；中文建置器重寫 Markdown 時，也移除了先前讓 RNN/Kalman verifier 通過的兩個 `COMPLETE` 狀態句。
- **處理**：IEEE 直接以實際章名為錨點；RNN/Kalman 狀態改由 `build_thesis_docx.py` 產生，避免再依賴生成後手動修改。
- **研究影響**：修復來源到產出的同步機制，不改任何 evidence JSON 或模型結果。
- **狀態**：已解決。
## RDL-037：E11D 段落使 IEEE 稿超出 IoTaIS 頁數上限

- **階段**：E11D IEEE 重建驗證。
- **難題**：加入完整 E11D 段落後，IEEE PDF 由 7 頁變成 8 頁，超過 full paper 的 6–7 頁目標；結論另殘留「enclosure hypotheses remain unsupported」的過時概括。
- **處理**：合併 E11B/E11C/E11D 為一個次要機箱段落，保留每個假設決策與 H-ENC-04 必要數值；結論改成區分 geometry-only 負面結果與 role-semantic 正面結果。
- **研究影響**：只壓縮重複敘述，不刪除 adverse result、uncertainty 或非因果限制。
- **狀態**：已解決。
## RDL-038：頁數壓縮誤刪既有實驗的同步識別數字

- **階段**：IEEE 7 頁壓縮後驗證。
- **難題**：壓縮 E11 段落時保留了模型指標與決策，卻刪除 E11B 的 1,641 與 E11C 的 1,505 snapshot counts，使既有同步 verifier 失敗。
- **處理**：只補回兩個樣本數，不恢復冗長敘述；重新編譯後再次檢查頁數及 E11B/E11C/E11D。
- **研究影響**：證據本身未變，但顯示稿件壓縮也必須受自動同步檢查約束。
- **狀態**：已解決。
## RDL-039：正向相對結果不等於尾端誤差已可接受

- **階段**：E11D 後續改善研究設計。
- **難題**：H-ENC-04 相對 global mean 為 supported，但角色模型 MAE 仍為 1.6517 C、P95 為 5.4886 C；若直接在 E11D 上選鄰居數或混合權重，會把確認集變成調參集。
- **處理**：建立 E11E 開發 split 與完全未碰的 E11F 確認 split；候選 grid、絕對門檻、選擇順序與 no-go 規則都在 E11E 下載前固定。
- **研究影響**：目前只改變研究計畫，尚未產生改善結果；不得宣稱模型準確度已提升。
- **狀態**：進行中。
## RDL-040：最佳候選平均改善，但尾端誤差與覆蓋未同時改善

- **階段**：E11E 開發結果判讀。
- **難題**：`role_local_k5_p2` 將 MAE 由 1.1168 降至 1.0187 C，bootstrap CI 也高於零，卻把 P95 從 3.4900 增至 3.7699 C，且只贏 25/42，距門檻差一個感測器。
- **處理**：不把 26/42 放寬為 25/42，也不忽略 P95；依預註冊規則記為 `no_candidate_forwarded`，保留 E11F 完全未下載。
- **研究影響**：證明平均誤差與尾端／跨感測器穩健性是衝突目標；後續若研究 tail-aware 方法，必須使用新的開發 split，不能回頭重選 E11E grid。
- **狀態**：E11E 已決策，模型改善問題仍未解決。
### RDL-041：LaTeX 決策代碼與同步驗證器的表示衝突

- **難題**：IEEE 原始稿中的 `no_candidate_forwarded` 若不跳脫底線會使 LaTeX 編譯失敗，但 E11E 驗證器原先只接受未跳脫的字面值。
- **處理**：保留合法的 `no\\_candidate\\_forwarded` 排版，驗證時先將 LaTeX 底線跳脫正規化，再檢查同一決策語意。
- **研究影響**：僅修正文件層的表示相容性；資料雜湊、模型指標、閘門結果與 E11F 未存取狀態均未改變。
### RDL-043：E11G 使用已觀察開發資料的適應性偏差

- **難題**：E11G 的方法設計受到 E11E 尾端失敗啟發，因此即使改用 leave-one-day-out，也不能把結果視為全新外部驗證。
- **處理**：將 E11G 明確限制為 adaptive development；每一折只用訓練日選擇感測器規則，E11F 保持未存取，通過後仍須另行預註冊確認。
- **報告方式**：只報 out-of-fold 開發指標與失敗閘門，不使用「已驗證機箱泛化」等敘述。

### RDL-042：Python 反射被非函式 callable 中斷

- **難題**：第一次探查既有 E11E 模組介面時，`inspect.signature` 對匯出的 `defaultdict` 類型拋出 `ValueError`，沒有取得函式簽章。
- **處理**：將反射條件縮限為 `inspect.isfunction` 後再執行一次；後續只依公開函式介面整合，不重讀既有實作內容。
- **研究影響**：僅影響工程探查，未讀取 E11F、未改變資料或實驗判定。
### RDL-044：OpenSpec delta requirement 缺少識別碼

- **難題**：E11G delta spec 初稿雖有 `Requirement` 標題，但未包含驗證器要求的 `EVD-###` 識別碼，因此不被計入有效 requirement。
- **處理**：依現有序列補為 `EVD-024` 後重新驗證；研究問題、方法、門檻與停止規則完全不變。
- **研究影響**：屬規格追蹤格式錯誤，發生在實驗執行前，未造成資料洩漏。
### RDL-045：E11G 腳本入口缺少 repository root

- **難題**：以 `python3 scripts/run_aau_tail_safe_development.py` 執行時，`sys.path` 只有 `scripts/`，導致匯入既有 runner 前即出現 `ModuleNotFoundError: scripts`。
- **處理**：在匯入專案模組前，以腳本位置計算 repository root 並加入 `sys.path`；再次執行仍沿用相同預註冊協定。
- **研究影響**：失敗發生在讀取 E11E 與模型評估之前，沒有產生部分結果，也未存取 E11F。
### RDL-046：重用 bootstrap 函式的欄位命名不一致

- **難題**：E11G 完成折疊計算後，閘門讀取 `ci95_lower_c`，但既有 E11E bootstrap 公開介面實際回傳 `ci_95_lower_c`，因此在輸出前發生 `KeyError`。
- **處理**：以小型固定輸入確認公開回傳 schema，將實作與合成測試統一為 `ci_95_lower_c`，再從頭重跑所有折疊。
- **研究影響**：錯誤發生在決策與寫檔之前；未留下可被挑選的部分結果，E11F 仍未存取。
### RDL-047：DOCX 建置會覆寫先行追加的論文 Markdown

- **難題**：`build_thesis_docx.py` 會重新產生 `docs/thesis/thesis_draft_zh.md`；若只在建置前追加 E11G，來源段落會被覆寫，導致 DOCX/PPTX 已同步但後續中文 PDF 可能仍使用缺少 E11G 的 Markdown。
- **處理**：將 E11G Markdown 同步納入 DOCX 建置完成後的同一個 idempotent hook，再由更新後來源重建 PDF。
- **研究影響**：屬產物同步順序錯誤；E11G 資料、雜湊、指標、失敗閘門與 E11F 未存取狀態均未改變。
### RDL-049：環境缺少 `pdftotext`

- **難題**：最終中文 PDF 文字驗證嘗試使用 `pdftotext`，但目前環境未安裝該命令，檢查在開啟 PDF 前即失敗。
- **處理**：改用建置環境已具備的 Ghostscript `txtwrite` 裝置輸出文字，再搜尋 E11G 識別與凍結數值。
- **研究影響**：只影響驗證工具選擇，PDF 本身已成功建置，實驗資料與判定不變。

### RDL-048：同步驗證器未處理 build script 的間接來源連結

- **難題**：`build_thesis_docx.py` 與 `build_thesis_pptx.py` 透過共享 E11G hook 維持同步，但初版 verifier 仍要求兩個入口腳本本體重複 `0.8945` 與決策字串，造成假失敗。
- **處理**：入口腳本改驗證 hook 匯入，共享 hook 另驗證凍結數值與決策；避免為通過檢查而複製研究常數。
- **研究影響**：修正依賴關係的驗證方式，不改動來源內容或生成產物。
### RDL-050：Ghostscript `txtwrite` 透過 pipe 結束失敗

- **難題**：以 Ghostscript `txtwrite` 將 PDF 文字直接送入 pipe 時，裝置結束階段回報 `child refcount > 1`，搜尋端未取得可靠輸出。
- **處理**：改為先寫入 `/tmp/thesis_e11g.txt`，待 Ghostscript 正常關閉後再以 `rg` 搜尋；不修改 PDF。
- **研究影響**：僅影響 PDF 文字抽取路徑，其他來源與壓縮產物一致性已通過。
### RDL-051：中文 PDF 不使用論文 Markdown 作為建置輸入

- **難題**：Markdown 已確認含 E11G，但 `build_thesis_pdf.py` 直接呼叫 `build_thesis_docx.build_blocks()` 產生 TeX，因此建置成功的 PDF 仍沒有 E11G。
- **處理**：在 `build_thesis_docx.py` 定義共用 `e11g_blocks()`，PDF 建置於既有 blocks 後加入同一凍結內容；DOCX 仍由 idempotent hook 同步。
- **研究影響**：修正 source-of-truth 接線，不改變任何研究數值、閘門或結論。
### RDL-052：Ghostscript 暫存文字含 NUL 位元

- **難題**：PDF 文字已成功抽取，但 Ghostscript `txtwrite` 輸出包含 NUL，`rg` 預設只顯示 `binary file matches`，無法直接呈現匹配內容。
- **處理**：使用 `rg -a` 將暫存輸出視為文字，分別確認 `E11G tail-safe` 與 `0.8945°C` 均存在於中文 PDF 抽取內容。
- **研究影響**：PDF 同步證據已取得；問題只涉及文字檢查工具的輸出編碼。
### RDL-054：新 AAU 開發分割可能與既有 byte ranges 或 E11F 重疊

- **難題**：AAU 公開檔案以固定 byte range 抽樣，若只靠人工記憶選 offset，可能重複 E11B–E11G 資料或誤觸保留的 E11F。
- **處理**：E11H downloader 在任何下載前遞迴掃描所有 enclosure manifest，並把 11 個 E11F 範圍加入 occupied intervals；任一交集即硬停止。
- **研究影響**：下載前的資料獨立性保護，實際範圍尚須通過檢查才可存取。

### RDL-053：commissioning 改善會改變研究主張的適用條件

- **難題**：使用目標位置前兩日真值做 residual calibration，可能提高準確率，但已不再是 zero-shot 稀疏空間重建。
- **處理**：將 E11H 明確定義為「短期 NTC／參考感測器 commissioning 後的虛擬感測器」，時間切分為 2 日校正、1 日選擇、後續凍結測試。
- **報告方式**：若通過，只能支持 calibration-assisted predictive evidence；硬體校正誤差與 E11F 泛化仍需獨立驗證。
### RDL-056：E11H 多個 Huber affine slope 落在限制邊界

- **難題**：E11H 雖通過測試閘門，但多個感測器的 Huber slope 達到預註冊下限 0.5，且 intercept 絕對值偏大，顯示窄溫度範圍下 slope/intercept 可識別性有限。
- **處理**：E11F 完全凍結參數，不重新估計；論文將此列為 extrapolation 風險，不把低誤差解讀為物理熱傳係數。
- **研究影響**：限制部署範圍與機制解釋，但不否定 E11H 凍結測試結果。

### RDL-055：byte-range 獨立不等於 calendar-day 獨立

- **難題**：E11H 與 E11G raw bytes 無重疊，但解析後部分日期相同；同一 campaign 的系統狀態可能高度相關。
- **處理**：E11F 預註冊強制報告日期交集，所有資料仍納入，不事後排除；確認主張限制為 unseen-byte within-campaign transfer。
- **研究影響**：即使 H-ENC-05 通過，也不能宣稱跨日期、跨機箱或外部場域泛化。
### RDL-058：H-ENC-05 通過但證據層級仍低於跨機箱驗證

- **難題**：E11F 的 frozen no-refit 指標與 39/42 覆蓋均通過，但資料仍來自同一 AAU campaign，且 calendar days 與開發資料重疊。
- **處理**：正式決策命名為 `h_enc_05_supported_within_campaign`，同步文件禁止省略後綴或改寫成 external enclosure validation。
- **後續需求**：若要回答「電腦機箱環境可用」，仍需實體機箱、NTC 校正鏈、不同負載／風扇狀態與跨日測試。

### RDL-057：E11F 一旦存取即失去未見確認集資格

- **難題**：E11F 已在預註冊通過後一次性下載與評估，後續任何 E11F-driven 調參都會污染確認證據。
- **處理**：凍結 manifest、raw fragment 與 result hashes；runner 記錄 `refit_performed=false`，未來模型改進必須使用新資料來源。
- **研究影響**：E11F 可支持本次 H-ENC-05 決策，但不能重複用作下一模型的確認集。
### RDL-059：E11H/E11F 同步使 IEEE 稿件增至 8 頁

- **難題**：新增 confirmation 結果與一筆 calibration 文獻後，IEEE PDF 第 8 頁只剩兩筆參考文獻，超過 IoTaIS 6–7 頁目標。
- **處理**：保留 E11B–E11F 的關鍵數值、假設判定與 claim boundary，壓縮 enclosure 敘述並移除非必要的新 bibliography entry；不刪除日期重疊、NTC 未驗證或 cross-enclosure 限制。
- **研究影響**：僅改善投稿排版密度，不改變研究證據或結論。
### RDL-060：IEEE 語意敘述缺少凍結決策代碼

- **難題**：IEEE 已寫明 H-ENC-05 只在同 campaign 支持，但沒有 evidence 使用的完整機器可驗證代碼 `h_enc_05_supported_within_campaign`。
- **處理**：在同一限制句加入 LaTeX 跳脫後的決策代碼，保留日期重疊、NTC 與 cross-enclosure 未驗證敘述，再檢查頁數。
- **研究影響**：改善跨來源可追蹤性，不改變判定。
### RDL-061：E11G verifier 將「當時未存取」誤寫成「永遠不得存在」

- **難題**：E11G 正確記錄 `e11f_accessed=false`，但舊 verifier 直接要求 E11F manifest 不存在；E11H 合法晉級後的一次性 E11F confirmation 因而造成假失敗。
- **處理**：改驗證研究時間序列：E11G access flag 仍為 false；後續 E11F 必須晚於 E11G、引用凍結 E11H hash 且 `refit_performed=false`。
- **研究影響**：保留 E11G 當時的未見資料狀態，同時允許預註冊通過後的合法確認存取。

### RDL-062：同步任務文字差異造成精確補丁失敗（2026-08-23）

- **難題**：E11H 與 E11F 任務清單的同步項目語意相同但措辭不同，第一次依假設文字套用補丁時無法匹配。
- **影響**：若自動化流程只依賴固定句子，文件措辭的小幅變動就會阻斷研究收尾；本次失敗發生在寫入前，未修改任何檔案。
- **處理**：只搜尋兩份任務檔中未勾選的核取方塊，再使用實際文字進行最小補丁，之後 OpenSpec 驗證通過。
- **後續**：任務自動化應優先依穩定識別碼或結構欄位定位，不應把自然語言句子當成唯一鍵。

### RDL-063：公開資料版本凍結與受限網路（2026-08-24）

- **難題**：沙箱內無法解析 `raw.githubusercontent.com`，而 GitHub `master` 分支 URL 可變；一次 commit API 查詢亦在使用者中斷前長時間未完成。
- **影響**：只記錄分支網址不足以重現資料，且自動下載可能因執行環境網路政策失敗。
- **處理**：經明確網路授權下載完整小型 CSV，並將每個檔案的來源、大小與 SHA-256 凍結；後續摘要不依賴可變分支內容。
- **後續**：若上游位元變動，流程必須 fail closed，不能自動覆寫既有研究證據。

### RDL-064：跨量測檔 schema 漂移（2026-08-24）

- **難題**：早期與晚期 BMC CSV 的欄位數不同，例如晚期資料增加 PSU 電流欄位，且檔案含 InfluxDB `#group`、`#datatype`、`#default` 中繼列。
- **影響**：依固定欄位位置解析會錯讀溫度或直接失敗，形成不易察覺的資料污染。
- **處理**：E12 依欄名解析、忽略註解列、只要求預註冊核心欄位，並禁止對缺值靜默插補。
- **後續**：結果需報告每檔有效列數與剔除原因，避免只呈現成功解析的子集。

### RDL-065：研究規格格式不能直接套用通用 OpenSpec（2026-08-24）

- **難題**：初版 E12 變更缺少 `research-first` schema marker，delta spec 未使用一級標題與倉庫要求的 EVD 編號，導致驗證器拒絕。
- **影響**：即使研究問題與 protocol 完整，規格仍無法被 canonical workflow 接受，後續證據也無法合法同步。
- **處理**：參照已通過的 E11H 變更，補上 `.openspec.yaml`、`# Evaluation and Evidence Delta`，並接續使用 EVD-027/EVD-028。
- **後續**：新研究變更應從 `research-first` 骨架建立，而不是從一般 OpenSpec 慣例推測格式。

### RDL-066：程式無數值洩漏仍可能違反測試隔離程序（2026-08-24）

- **難題**：初版 runner 先把 final-test CSV 解析到記憶體，再呼叫未引用 test rows 的選模函式；數值結果沒有直接洩漏，但不符合「先落盤凍結、再開啟測試檔」的嚴格 protocol。
- **影響**：研究者無法由執行順序證明測試資料在選模時不可見，削弱外部確認的可信度。
- **處理**：正式 run 前主動停止，將 API 拆成 `select_and_refit` 與 `evaluate_frozen`；runner 必須先寫出 frozen-model JSON 與雜湊，之後才載入 test split。
- **後續**：防洩漏不應只檢查函式是否使用資料，也要檢查資料何時被開啟、模型何時被持久化。

### RDL-067：從 scripts 路徑直接啟動時找不到專案模組（2026-08-24）

- **難題**：以 `python3 scripts/run_bmc_cross_run_e12.py` 啟動時，Python 的搜尋路徑以 `scripts/` 為首，無法匯入 repository root 下的 `digital_twin`。
- **影響**：第一次正式命令在 import 階段終止；尚未讀取 manifest 或 final-test，因此沒有模型選擇或結果污染。
- **處理**：runner 依 `__file__` 計算 repository root 並明確加入 `sys.path`，不改資料、模型、切分與門檻。
- **後續**：直接執行的研究 scripts 應有一致的 root bootstrap，或統一改為 module entry point。

### RDL-068：完整量測檔不一定有 30 筆可用 BMC rows（2026-08-24）

- **難題**：E12 預註冊每檔至少 30 筆有效列，但 2 個 training runs 與 3 個 selection runs 僅有 13–27 筆，正式命令在第一個失敗檔即停止。
- **影響**：H-ENC-06 無法進入選模與 final test，不能產生或宣稱任何準確度結果。
- **處理**：保留 E12 為 `h_enc_06_not_supported`；診斷僅讀取 train/selection，確認 17 個 development files 均至少 13 筆，14 個 final-test files 保持未開啟。
- **後續**：另立 E13，預先固定 10-row availability gate；E12 失敗不被覆寫，E13 亦不得變更原準確度門檻。

### RDL-069：統計極端值實為跨 section schema 錯位（2026-08-24）

- **難題**：E13 出現數百億度與約 6,500 萬度模型誤差，初步可能被誤判為感測器 sentinel 或重尾 outlier。
- **影響**：若直接套 Huber、clipping 或 outlier deletion，會掩蓋真正的資料語意錯誤，產生看似合理但不可重現的結果。
- **處理**：追查 raw CSV 發現同檔有多個 `#group` 與不同 header；host row 的 CPU counters 被固定 BMC header 錯映射。上游 `split.py` 亦證實必須先分 section，再區分 `bmc` 與 `host`。
- **後續**：parser correctness 必須獨立驗證；任何 robust method 只能在 schema 正確後比較。

### RDL-070：修正 parser 後原 E13 test 已不再是未見資料（2026-08-24）

- **難題**：E13 已依錯誤 parser 開啟並評估 14 個 final-test runs；根因分析也已查看其中的極端時間點。
- **影響**：即使只修 parser、不改模型，重新使用同一批 runs 也只能算 retrospective sensitivity analysis，不能稱為外部確認。
- **處理**：保留 E13 原始結果與 invalidation 原因，將 parser 修正獨立成 E14A，並要求後續 confirmation 從上游尚未使用的完整 runs 重新預註冊。
- **後續**：報告需區分原始失敗、修正後探索分析與真正未見 confirmation 三種 evidence level。

### RDL-071：parser correctness 容易形成循環驗證（2026-08-24）

- **難題**：若 production parser 與驗證器共用相同 section helper，31/31 一致可能只是同一錯誤被重複兩次。
- **影響**：表面完整的測試仍無法證明 BMC/host 語意真的被分離。
- **處理**：E14A 預註冊兩個分離實作：production parser 產生 normalized rows，oracle 只依 raw-line local header 位置計數；另加入已知 host timestamp 排除測試。
- **後續**：correctness evidence 同時要求 count agreement、row identity、source tags 與極值 sanity，不只檢查單一總列數。

### RDL-072：synthetic fixture 本身可能製造假 parser 失敗（2026-08-24）

- **難題**：E14A 初次聚焦測試有兩個 fixture 失敗；舊 fixture 缺 `_measurement/device_id`，新 fixture 的多行字串意外保留 patch marker `+`，使 `#group` 不在行首。
- **影響**：測試資料不符合預註冊 schema，無法判斷 production parser 是否正確，且可能誤導研究者修改正確邏輯。
- **處理**：把 source columns 與 numeric columns 分開定義，兩個 fixture 都明示 `sdgp/bmc`，並移除字串內的 patch marker。
- **後續**：parser tests 必須先驗證 fixture 的原始 section/header 形狀，再驗證 normalized rows。

### RDL-073：同名 BMC 欄位混合已換算值與 raw hwmon 單位（2026-08-24）

- **難題**：source-aware parsing 後仍有三檔溫度 median 52,000–54,000、功率 median 2.6–3.2 億；其餘 28 檔分別為 32.5–67.5 與 239–431。
- **影響**：欄名相同但缺少 Scale metadata，直接合併會讓模型尺度、係數與誤差完全失真；E14A 因 ≥1,000°C gate 失敗。
- **處理**：查核 Linux hwmon 與 OpenBMC 官方文件，確認 millidegree Celsius、microwatt 與 `Scale=-3` 慣例；另立 E14B，以 section median 一次判定 regime，不逐 row 猜測。
- **後續**：單位指標必須溫度／功率一致，倍率與三個 raw-unit 檔名預先固定；任何不一致都保留為 null outcome。

### RDL-074：資料修正成功不等於模型確認恢復（2026-08-24）

- **難題**：E14B 已使數值回到物理範圍，但 E13 的 test files、極端時間點與結果均已被研究者看過。
- **影響**：修正 parser 後重跑同一 split 即使表現良好，也存在方法選擇與敘事偏誤，不能重新命名為 unseen confirmation。
- **處理**：另立 E14C 並固定沿用原候選與 gates，只輸出 candidate eligibility；真正確認必須換成未使用完整檔案。
- **後續**：同步文件需明列 data correctness、retrospective sensitivity、new confirmation 三個 evidence tier。

### RDL-075：強時間外推同時提高證據力與失效風險

- **日期**：2026-08-24
- **階段**：E15 預註冊
- **難題**：若只用鄰近日期，確認較容易通過但外推價值有限；若加入 2024 Jenkins 等較晚工作負載，則模型漂移、控制策略改變與新單位制度可能同時出現，失敗原因較難拆解。
- **處理**：固定 14 個檔案且禁止事後替換；在準確度閘門前保留逐 section 單位一致性、每檔最少列數、有限值與預測範圍閘門，並以完整 run 為 bootstrap 單位。
- **報告意義**：這是研究效度與通過機率的取捨。選擇較強外推可產生更可信的正結果，也能讓負結果指出模型實際適用邊界。

### RDL-076：E15 delta spec 缺少驗證器要求的一級標題

- **日期**：2026-08-24
- **階段**：E15 OpenSpec 驗證
- **難題**：研究內容與情境格式完整，但新 delta spec 直接從 `## ADDED Requirements` 開始，未符合儲存庫驗證器要求的 level-1 title。
- **處理**：在 requirements 前補上 E15 專屬一級標題，保持預註冊假設、檔案、模型與閘門不變後重新驗證。
- **報告意義**：機器可驗證的研究紀錄不只檢查方法內容，也要求一致的文件結構；格式失敗應在讀取結果前修正並留痕。

### RDL-077：E15 下載授權在執行介面被拒絕

- **日期**：2026-08-24
- **階段**：E15 資料取得
- **難題**：研究規格與 focused tests 已通過，但下載 14 個預註冊公開 BMC CSV 的提權請求被拒絕，因此不能在今天的報告前產生 E15 結果。
- **處理**：停止下載與評估，不以其他檔案替代、不重用已開啟資料，也不填寫預期 evidence；報告只呈現截至 E14C 的實際結果及 E15 的預註冊狀態。
- **報告意義**：外部資源與權限也是可重現研究的實際限制。正確處理是保留缺失結果與中斷原因，而不是為了完成報告而補造數值。

### RDL-078：預設 Python 環境缺少簡報建置套件

- **日期**：2026-08-24
- **階段**：今日研究進度簡報建置
- **難題**：報告講稿與簡報 source 已完成，但預設 `python3` 執行時缺少 `python-pptx`，儲存庫與 `/tmp` 也沒有可重用的既有虛擬環境。
- **處理**：保留已完成的 Markdown 報告；嘗試把單一建置相依套件安裝到 `/tmp` 隔離目錄，不修改專案依賴或全域 Python 環境。
- **報告意義**：研究交付物也需要可重現的建置環境。內容完成與輸出格式生成應分開記錄，避免把工具鏈失敗誤報成研究內容未完成。

### RDL-079：簡易 GRU／LSTM 比較仍需控制模型容量

- **日期**：2026-08-24
- **階段**：GRU／LSTM 簡易比較預註冊
- **研究難題**：若 GRU、LSTM 直接沿用 vanilla RNN 的 hidden units，門控結構會多出約三到四倍參數；即使結果較好，也無法區分是 gating 有效還是單純模型較大。
- **處理**：在讀取新結果前固定 vanilla RNN 6 units、GRU 3 units、LSTM 2 units，參數量約 148、169、140；三者共用 4 筆歷史、30 epochs、Adam、seed 42、相同 train/test endpoints 與四目標輸出。
- **報告意義**：這次只做單一 seed 的輕量篩選。通過門檻只能把模型送進後續完整 3D 比較，不能宣稱 GRU 或 LSTM 普遍優於其他方法。

### RDL-080：OpenSpec requirement ID 不接受語意型後綴

- **日期**：2026-08-24
- **階段**：GRU／LSTM OpenSpec 驗證
- **難題**：delta spec 使用 `RGV-RNNGATE-01` 與 `SYN-RNNGATE-01`，內容完整但不符合驗證器要求的 capability 加連續數字格式。
- **處理**：只把 ID 改為 `RGV-009` 與 `SYN-012`，假設、模型設定、資料切分和判定門檻完全不變，再重新驗證。
- **報告意義**：研究規格的穩定識別碼也屬於可追溯性的一部分；格式修正必須與實驗內容變更分開記錄。

### RDL-081：門控模型正常收斂，但測試仍不如線性與慣性基準

- **日期**：2026-08-24
- **階段**：GRU／LSTM 簡易同資料正式比較
- **研究難題**：GRU 與 LSTM 在三個 horizon 的 standardized training MSE 都下降且無非有限值，但六方法最低 MAE 仍由 sequence linear regression 取得 7/12、persistence 取得 5/12；GRU/LSTM 均為 0/12。
- **處理**：保留完整負結果。GRU 只在兩個 60 分鐘濕度案例勝 vanilla RNN（2/12），中位相對改善 -12.880146%；LSTM 為 0/12 與 -11.368865%。依預註冊規則不增加 hidden units、不換 seed、不延長 history，也不重跑取較佳結果。
- **研究解讀**：四筆歷史的 SML2010 absolute-value task 主要由短期線性關係與時間慣性主導，簡易 gated recurrence 沒有形成額外價值。這只否定目前固定容量與單一 seed 設定，不等同否定所有 GRU/LSTM；任何多 seed、長 history 或 3D 比較必須另立新 protocol。
