# Hardware Documentation

本目錄整理三因子感測節點與房間部署規劃。

- `three_factor_sensor_node_zh.md`：ESP32-C3 + DHT11 + BH1750 的 v1 感測節點設計。
- `sensor_node_bom_estimate_zh.md`：單顆 node 與 6 / 8 / 10 / 12 / 14 顆部署成本估算。

目前硬體定位：

- 低成本 sparse sensing node。
- 支援 `input` / `validation` roles。
- 用於真實房間 target-point validation。
- DHT11 不作高精度實驗室 reference。
- BH1750 優先作為正式照度 lux sensor。
