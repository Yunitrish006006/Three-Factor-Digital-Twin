# Executed evidence

執行日期2026-10-05。事先固定 protocol/config，再校準36回合、凍結source snapshots，正式48回合5760步；合計10080步。原v1完整保留。

## Actual decisions

H-CTRL-01 SUPPORTED_SIMULATION_ONLY；H-CTRL-02 NOT_SUPPORTED；H-CTRL-03 NOT_SUPPORTED。holdoutfixed/PID+FF/LQR/MPC MAE=2.9051/1.7713/1.7304/1.8071°C；fanproxy=.7200/.9832/1.0034/1.0567Wh。MPC相對PID+FF為-2.0193%、相對LQR為-4.4310%改善。

正式MPC殘差拒絕回退7步：validation121/122/123各1/1/3步，plant_holdout143兩步。所有solverstatus雖solved，但primal residual>1e-5，依固定gate拒絕。無input/slew違例或deadline。過載0/360numericfallback，仍取樣超溫；不能稱安全。three variants不支持跨實體設備泛化。

## Actual checks and reproducibility

- verification.json：stdlib獨立全metrics/選參/decision/初始與scenario/plant/ZOH prediction/來源freeze與時間順序，84回合10080步PASS。
- adversarial_tests.log與optimized.log：6拒絕篡改/marker failure tests，normal與-O都PASS。
- repository_tests.log：304 tests/28.736s OK。E15相關測試僅mockfixtures，不執行消耗過的一次性研究。
- source_snapshots含完整8研究來源；result SHA256=a8ec78210a901041db17a47c76a0e010bcf497ccad3610b57a6dbaea9c61f1d3。
- multistep_model_diagnostic.json：預先指定12step rampup/down。末端MAE .12956/.60101°C，只是名義模型診斷，不是實測。
- docx/pdf/pptx/ieee_build.log：既有canonicalbuilders重建成功，IEEE7頁。DOCX/PDF指定副本binary一致、PPTX兩份各有一頁v2、outlines/builder相符。
- HTML教授主報告與v2details單檔離線，實際瀏覽1440/820/390寬度、錨點、展開鍵盤、表格局部overflow、console檢查；新PDF頁89與IEEE頁7目視檢查。完整Office全頁視覺QA未完成。

## Deviations and uncompleted work

Precalibration數值單點診斷需要增加共用maxiter/rho/降低infeasibility tolerance，已在protocol amendment於正式freeze前記錄；未用正式結果重調。三角色初審完成，followup寫入中因服務用量限制中止，父代理接手；不聲稱修正後三角色再審完成。

documents/presentations技能指定bundled LibreOffice，當前工具沒有load_workspace_dependencies、runtime技能或bundledsoffice；遵照不改用使用者desktopLibreOffice，Office全頁visualQA保持pending。實機NTC/RPM/負載量測與設備連線未提供，E8/physical_enclosure/NTC NOT_EVALUATED。未commit/push/publication。
