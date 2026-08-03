# 系統架構圖

本文件將目前單房間三因子空間數位孿生原型的實作架構整理成 GitHub 可直接顯示的 Mermaid 圖表，方便用於 README、論文方法章、口試簡報與系統說明。

正式論文與簡報輸出的 SVG 由 `scripts/build_architecture_diagrams.py` 產生。該腳本目前使用統一的 16:9 local SVG renderer，讓研究整體邏輯圖、圖 3-1、圖 3-2、圖 3-3、圖 3-4、圖 3-5 與圖 5-1 保持相同字級、色彩、框線與箭頭風格。研究整體邏輯圖先回答「研究問題如何連到方法、證據與有界結論」，既有系統分層圖再回答「系統責任如何分層」。下方 Mermaid 區塊保留作為語意草稿與 GitHub 預覽。

## 1. 研究整體邏輯架構

```mermaid
flowchart LR
    GAP["研究缺口<br/>稀疏 IoT 感測 + 非連網家電<br/>仍需理解 T/H/L 空間分布與裝置影響"]

    RQ1["RQ1 空間場估計<br/>8 角點能否支援 T/H/L 場？"]
    M1["變數專屬 nominal model<br/>power calibration + trilinear correction<br/>optional hybrid residual"]
    E1["E1-E3 / E6 / E7<br/>controlled field + IDW + LOO<br/>real pillow hold-out"]
    C1["有界結論<br/>受控完整場與真實未見點改善<br/>不等同任意房間 dense truth"]

    RQ2["RQ2 裝置影響學習<br/>能否由環境變化學習非連網裝置？"]
    M2["before / after delta + spatial basis<br/>AC / window / light impact learning"]
    E2["E4 / E5 / E9 event tasks<br/>impact check + window matrix<br/>public aligned response"]
    C2["有界結論<br/>structured impact prior 有效<br/>不等同真實因果識別"]

    RQ3["RQ3 決策支援<br/>能否輸出可解釋候選動作排序？"]
    M3["point / zone + complete T/H/L target<br/>counterfactual rerun + comfort penalty"]
    E3["目前：model-based ranking<br/>E8：future intervention protocol"]
    C3["有界結論<br/>可提供反事實決策支援<br/>尚未證明實際因果改善"]

    RQ4["RQ4 標準化服務（secondary）<br/>能否讓 AI client 使用同一模型？"]
    M4["shared service path<br/>scripts / Web / MCP + Gemma bridge"]
    E4["functional tests + demo<br/>非獨立量化實驗"]
    C4["有界結論<br/>介面重用同一 estimator<br/>不作 headline novelty"]

    GAP --> RQ1 --> M1 --> E1 --> C1
    GAP --> RQ2 --> M2 --> E2 --> C2
    GAP --> RQ3 --> M3 --> E3 --> C3
    GAP -. secondary .-> RQ4 -.-> M4 -.-> E4 -.-> C4
```

這張圖是整篇論文的 argument map，而不是另一張 runtime flow。閱讀順序固定為：

1. 一般房間同時面臨稀疏感測與非連網裝置限制。
2. RQ1--RQ3 構成主要研究線，RQ4 是服務化的次要系統線。
3. 每個研究問題都必須對應到方法與明確證據層。
4. 結論只能落在證據能支持的範圍；controlled、real snapshot、public aligned 與 future intervention 不可互換。

## Overall Research Logic Architecture

```mermaid
flowchart LR
    GAP["Research gap<br/>Sparse IoT sensing + non-networked appliances<br/>Spatial T/H/L fields and appliance impacts remain unknown"]
    RQ1["RQ1 Spatial field estimation"] --> M1["Variable-specific model"] --> E1["E1-E3 / E6 / E7"] --> C1["Bounded field-estimation claims"]
    RQ2["RQ2 Appliance-impact learning"] --> M2["Before / after impact"] --> E2["E4 / E5 / E9 event tasks"] --> C2["Structured impact prior, not causality"]
    RQ3["RQ3 Decision support"] --> M3["Counterfactual ranking"] --> E3["Current / E8 future protocol"] --> C3["Ranking support, not proven intervention gain"]
    RQ4["RQ4 Standardized service<br/>(secondary)"] -.-> M4["Shared service path"] -.-> E4["Functional evidence"] -.-> C4["Secondary contribution"]
    GAP --> RQ1
    GAP --> RQ2
    GAP --> RQ3
    GAP -.-> RQ4
```

此英文對應圖與中文研究整體邏輯圖使用相同的節點、證據邊界與版面，專供 IEEE 稿使用，避免英文論文出現中文主圖。

## 2. 整體分層架構

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    ROOT["單房間三因子空間數位孿生系統<br/>Sparse IoT sensing + non-networked appliances"]

    ROOT --> OBS["情境與觀測層<br/>room state enters one shared path"]
    ROOT --> MODEL["估測與學習層<br/>interpretable model first"]
    ROOT --> SERVICE["服務與決策層<br/>same estimator, multiple access surfaces"]

    OBS --> ROOM["Room schema<br/>geometry / zones / furniture blockers"]
    OBS --> SENSOR["Sparse IoT evidence<br/>8 corner sensors / outdoor + time"]

    MODEL --> FIELD["T/H/L field model<br/>bulk + local field / device influence"]
    MODEL --> LEARN["Calibration + learning<br/>power scale / trilinear / impact + hybrid residual"]

    SERVICE --> TOOLS["Tool interfaces<br/>scripts / Web / MCP + Gemma bridge"]
    SERVICE --> OUT["Decision outputs<br/>point / zone / 3D / action ranking"]
```

## 3. 主要執行資料流

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 22, 'rankSpacing': 32}} }%%
flowchart TB
    A["User input\nscenario / devices / environment / timeline"]

    subgraph Entry["Entry layer"]
        direction LR
        B1["web_demo.py"]
        B2["MCP tool call"]
    end

    subgraph Build["Scenario build"]
        direction LR
        C["core/service.py"] --> D["Build base scenario"]
        D --> E["Apply overrides\ndevices / furniture / baseline"]
    end

    subgraph Estimate["Estimation path"]
        direction LR
        F["DigitalTwinModel.simulate()"] --> G["Field + sensor prediction"]
        G --> H["Power calibration\n+ trilinear correction"]
        H --> I["Zone averages / point samples"]
    end

    subgraph Output["Output"]
        direction LR
        M["Hybrid residual correction"] --> N["Action ranking + dashboard / MCP"]
    end

    A --> Entry
    Entry --> Build
    Build --> Estimate
    Estimate --> Output
```

## 4. 感測器校正與學習流程

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    T1["Truth-adjusted devices"] --> T2["Truth simulation"]
    T2 --> T3["Synthetic 8-corner sensor observations"]

    B1["Nominal device settings"] --> B2["Nominal simulation"]
    B2 --> B3["Predicted sensor values"]

    T3 --> C1["Sensor residuals"]
    B3 --> C1

    C1 --> C2["Active device power calibration"]
    C2 --> C3["Trilinear residual correction<br/>8 parameters"]
    C3 --> C4["Corrected field reconstruction"]

    T3 --> L1["Before / after observations"]
    B2 --> L1
    L1 --> L2["Least-squares appliance impact learning"]

    C4 --> R1["Target-zone estimates"]
    L2 --> R2["Learned appliance impact coefficients"]
    R1 --> R3["Action ranking / recommendation"]
```

## 5. 模型學習推論與推薦資料流

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 18, 'rankSpacing': 28, 'curve': 'basis'}} }%%
flowchart LR
    subgraph Train["A. Learning and training path"]
        direction TB
        T0["Raw records<br/>corner sensors / device events / outdoor / scenario"] --> T1["Time alignment<br/>unit and coordinate normalization"]
        T1 --> T2["Scenario state assembly<br/>baseline + outdoor + devices + furniture + time"]
        T2 --> T3["Nominal field estimate<br/>temperature / humidity / illuminance"]
        T3 --> T4["Sparse calibration<br/>power scale + trilinear residual"]
        T4 --> T5{"Training branch"}
        T5 --> T6["Impact learning<br/>before-after delta + device spatial basis"]
        T5 --> T7["Hybrid residual learning<br/>features + residual labels"]
        T6 --> A1[("Learned impact coefficients")]
        T7 --> A2[("Residual checkpoint")]
        T7 --> A3[("Validation summary JSON")]
    end

    subgraph Runtime["B. Runtime inference and recommendation path"]
        direction TB
        R0["Runtime input<br/>MCP / web demo / script / API"] --> R1["Scenario override and validation<br/>baseline + devices + furniture + time"]
        R1 --> R2["Nominal T/H/L estimate<br/>variable-specific physical models"]
        R2 --> R3["Sparse correction<br/>registered sensors or calibration state"]
        R3 --> R4["Optional hybrid residual<br/>add learned residual if checkpoint exists"]
        R4 --> R5["Point or zone prediction<br/>temperature + humidity + illuminance"]
        R5 --> R6["Recommendation precondition<br/>point sample or cluster sample + T/H/L target"]
        R6 --> R7{"Complete scope + target?"}
        R7 -- "No" --> R8["Return prediction<br/>or missing-target error"]
        R7 -- "Yes" --> R9["Counterfactual action simulation<br/>rerun inference for each candidate"]
        R9 --> R10["Rank by comfort penalty reduction<br/>recommended device operation"]
    end

    A1 -. "device impact coefficients" .-> R3
    A2 -. "optional residual model" .-> R4
    A3 -. "reproducible evidence" .-> R10
```

## 6. 可模組化裝置與家具架構

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    D["Device sources<br/>built-in devices + device_specs + extra_devices"]
    F["Furniture sources<br/>built-in furniture + extra_furniture"]
    D --> S["Scenario state"]
    F --> S
    S --> M["DigitalTwinModel"]
    M --> E1["Device local effects"]
    M --> E2["Bulk room state"]
    M --> E3["Obstacle-aware attenuation"]
    E1 --> R["Spatial field output"]
    E2 --> R
    E3 --> R
```

## 7. 房間感測器與目標區域配置

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 18, 'rankSpacing': 24}} }%%
flowchart LR
    subgraph Room["Standard room topology (6 m x 4 m x 3 m)"]
        direction LR

        subgraph Ceiling["Ceiling layer sensors"]
            direction LR
            CSW["ceiling_sw"]
            CSE["ceiling_se"]
            CNW["ceiling_nw"]
            CNE["ceiling_ne"]
        end

        subgraph Devices["Main devices"]
            direction LR
            WIN["window_main<br/>left wall"]
            LGT["light_main<br/>ceiling center"]
            ACM["ac_main<br/>right wall"]
        end

        subgraph Zones["Target zones"]
            direction LR
            ZW["window_zone"]
            ZC["center_zone"]
            ZD["door_side_zone"]
        end

        subgraph Floor["Floor layer sensors"]
            direction LR
            FSW["floor_sw"]
            FSE["floor_se"]
            FNW["floor_nw"]
            FNE["floor_ne"]
        end
    end

    Ceiling --> Devices
    Devices --> Zones
    Zones --> Floor
```

## 8. 驗證與實驗流程圖

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    A["Validation scenario\nroom + environment + devices + furniture"]

    subgraph Sim["Simulation"]
        direction LR
        B["Apply truth adjustments\nto active devices"] --> C["Truth simulation"]
        C --> D["Synthetic 8-corner observations"]
        D --> E["Nominal simulation\nwith original device settings"]
    end

    subgraph Corr["Correction"]
        direction LR
        F["Sensor-informed correction\npower calibration + trilinear residual"] --> G["Corrected estimate"]
        G --> H["Optional hybrid residual correction"]
    end

    subgraph Eval["Evaluation"]
        direction LR
        I["Reference builders\nIDW baseline + impact learning"] --> J["Compare outputs\ntruth vs corrected vs baseline"]
        J --> K["MAE metrics + action ranking\n+ exported summaries and figures"]
    end

    A --> Sim
    Sim --> Corr
    Corr --> Eval
```

## 9. 程式碼結構圖

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    REPO["Repository root"]
    REPO --> DT["digital_twin/"]
    REPO --> SCRIPTS["scripts/"]
    REPO --> TESTS["tests/"]

    DT --> CORE["core/<br/>entities / scenarios / service / demo"]
    DT --> PHY["physics/<br/>model / baselines / learning / recommendations"]
    DT --> NEU["neural/<br/>hybrid_residual"]
    DT --> MCP["mcp/<br/>mcp_server / gemma_bridge"]
    DT --> WEB["web/<br/>web_demo / render"]
```

## 10. 文件與輸出結構圖

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 28}} }%%
flowchart TB
    REPO["Repository root"]
    REPO --> DOCS["docs/"]
    REPO --> OUT["outputs/"]

    DOCS --> THESIS["thesis/"]
    DOCS --> MODELS["models/"]
    DOCS --> DMCP["mcp/"]
    DOCS --> DWEB["web/"]
    DOCS --> EXP["experiments/"]
    DOCS --> PAPERS["papers/ieee/"]
    DOCS --> ADMIN["admin/"]

    OUT --> DATA["data/"]
    OUT --> FIG["figures/"]
    OUT --> PAP["papers/"]
```

## 11. 圖表使用建議

- 若要放進 GitHub repo，直接保留 Mermaid 區塊即可。
- 若要先說清楚整篇論文的邏輯，優先使用第 1 張研究整體邏輯架構。
- 若要說明方法實作，再使用第 2 張系統分層、第 3 張執行資料流、第 4 張校正學習與第 5 張學習推論推薦資料流。
- 第 6 張適合放方法章或附錄，用來說明裝置與家具的可模組化設計。
- 第 9 張與第 10 張較適合 README、系統說明或口試備用頁，不建議放論文正文。
