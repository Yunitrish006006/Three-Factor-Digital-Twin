# NTC 測溫硬體可行性評估

## 結論

NTC 熱敏電阻可作本研究的低成本、多點室內／機箱測溫節點，但不宜在未校正時充當論文參考真值。建議把 NTC 用作待評估的稀疏感測硬體，以 TMP117 或校正過的 PT100 作共址參考。

## 建議硬體

- 感測元件：有原廠 R-T 表的 10 kOhm、R25 ±1% 線式小珠 NTC，例如 TDK `B57861S0103A039`；其 B25/100 為 3988 K ±1%、耗散常數 3.2 mW/C、工作範圍 -55 至 155 C。不要使用沒有料號、B 值容差與封裝資料的通用「3950 模組」。
- 分壓電阻：10 kOhm、±0.1%、低溫漂金屬膜電阻；若優先降低自熱，可改用 47 kOhm NTC 與同值分壓電阻，但需確認 ADC 對較高源阻抗的取樣穩定時間。
- ADC：原型可用 12-bit、8-channel MCP3208，並讓分壓供電與 `VREF` 共源形成 ratiometric 量測；高精度版可用具外部參考與 PGA 的 ADS122C04。若直接用 ESP32 ADC，必須啟用校正、輸入端加約 100 nF、重複取樣，不能假設每顆晶片都是理想 1.1 V 參考。
- 參考感測器：室溫範圍建議 TMP117；原廠規格在 -20 至 50 C 不校正即可達 ±0.1 C。需要探棒或表面量測時，改用 3/4-wire PT100 與適當 RTD 前端。

## 電路與演算法

以 NTC 接 `VREF`、固定電阻接地的分壓為例：

```text
VREF -- NTC --+-- ADC
              |
             Rref
              |
             GND
```

先由 ADC ratio 反算 NTC 電阻，再使用該料號的 Steinhart-Hart 係數或完整 R-T lookup table 換算溫度。B-parameter 單式只適合較窄範圍；正式分析應保存原始 ADC code、換算電阻、校正係數與溫度值。

10 kOhm + 10 kOhm 在 3.3 V、25 C 時，NTC 功率約 0.272 mW。若耗散常數為 3.2 mW/C，理想穩態自熱約 0.085 C；仍需用實測確認。可用 GPIO/analog switch 間歇供電，等待 ADC settling 後快速取樣，以降低平均自熱。

## 建議驗證程序

1. 製作至少 5 顆 NTC 通道與 1 顆 TMP117/PT100 參考通道。
2. 在約 15、20、25、30、35、40 C 做共址校正；每點達熱平衡後至少記錄 10 分鐘。
3. 校正集擬合每顆 NTC 的係數，另留溫度點作確認，不可用同一批資料同時校正與宣稱精度。
4. 報告 MAE、RMSE、bias、P95、通道間差異、反應時間與漂移；目標可先設 MAE <= 0.3 C、P95 <= 0.5 C。
5. 機箱測試要區分空氣溫度與表面溫度。空氣探頭懸空並隔離 PCB/電源熱源；表面探頭需固定接觸壓力、膠材與位置。

## 主要風險

- NTC 非線性、R25/B 容差與老化。
- 分壓器自熱、ADC 參考與量化誤差。
- 導線熱傳、PCB 熱源、氣流速度與封裝熱時間常數。
- 多顆感測器若未逐顆校正，空間差異可能只是通道 offset。
- TMP117 安裝在 PCB 上時也可能量到板溫，必須與 NTC 探頭真正共址並隔離熱源。

## 原廠資料

- [TDK B57861S0103A039](https://product.tdk.com/en/search/sensor/ntc/ntc_element/info?part_no=B57861S0103A039)
- [Vishay NTC application note](https://www.vishay.com/docs/29053/ntcappnote.pdf)
- [TI single-ended ADC NTC circuit](https://www.ti.com/lit/an/sbaa338a/sbaa338a.pdf)
- [Analog Devices thermistor system design](https://www.analog.com/en/resources/analog-dialogue/articles/thermistor-temperature-sensing-system-part-1.html)
- [Espressif ESP32 ADC calibration](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc/adc_calibration.html)
- [TI TMP117 datasheet](https://www.ti.com/lit/ds/symlink/tmp117.pdf)
- [Microchip MCP3208](https://www.microchip.com/en-us/product/MCP3208)
- [TI ADS122C04](https://www.ti.com/product/ADS122C04)

## 研究狀態

本文件是可行性評估，不代表論文方法已採用 NTC。正式納入實驗前，必須另開 research-first OpenSpec，預註冊硬體料號、校正／確認切分、安裝幾何、取樣週期與接受門檻。

