# Hardware Documentation

本目錄整理三因子感測節點、房間部署規劃、validation-grade sensor upgrade 與操作事件紀錄。

- `three_factor_sensor_node_zh.md`：ESP32-C3 + 溫濕度 sensor + BH1750 的三因子感測節點設計，包含 input-grade / validation-grade、fan-aware payload 與 node metadata。
- `sensor_node_bom_estimate_zh.md`：單顆 node 與 6 / 8 / 10 / 12 / 14 顆部署成本估算，包含 validation-grade sensor upgrade 與風扇狀態紀錄選項。
- `validation_grade_sensor_plan_zh.md`：SHT31 / SHT35 / SHT40 / SHT45 的 validation / reference 升級策略與預算。
- `../thesis/fan_effect_design_zh.md`：電風扇作為 dynamic airflow redistribution source 的論文處理方式。
- `../thesis/google_home_operation_logging_zh.md`：Google Home 控制紀錄作為 operation event log 的使用邊界。

目前硬體與資料定位：

- 低成本 sparse sensing node。
- 支援 `input` / `validation` roles。
- 用於真實房間 target-point validation。
- DHT11 可作 input-grade low-cost sensor，但不作高精度實驗室 reference。
- `S_validation` nodes 建議使用 SHT31 / SHT35 / SHT40 / SHT45 或同等級溫濕度 sensor。
- BH1750 優先作為正式照度 lux sensor。
- 電風扇狀態需以 manual log、Google Home UI log、smart plug 或其他安全方式標記，fan-on 與 fan-off 不混算。
- Google Home 可作為冷氣、風扇與照明的操作事件來源，但不取代感測器與 validation truth。
