# 多角色審查與修正紀錄

## 真正執行的角色

2026-10-05 三個 readonly 初審已完成：
- control_review：methodology-analyst，控制理論、求解與LQR；要求模型gpt-6-astra/high。
- engineering_review：independent-reviewer，失敗處理與可重現性；要求模型gpt-6-astra/high。
- evidence_review：independent-reviewer，公平比較、主張與文件；要求模型gpt-6-astra/high。

模型欄記錄spawn要求，不另外聲稱有backend runtime證明。後續three evidence-extractor角色有寫入檔案，但被服務用量限制中止；父代理接手修正與驗證，不把它算成已完成的修正後獨立三角色再審查。

## 發現、修正與仍有限制

|初審問題|處理|真正證據|
|---|---|---|
|v1 overload190/360回退，全部linesearch問題|v2 OSQP、scaledslack/ZOH、strict原約束/residual gates；先單點診斷後凍結|v2 overload0/360回退；validation5/360、plantvariants2/360殘差拒絕回退，全保留|
|一風扇不能同時達CPU/GPU兩目標|sharedbounded equilibrium allocation、可達x_eq、DARE檢查|12 controller tests；不宣稱飽和後全域最優穩定|
|verify未獨立timing/H2、校準重用runner metrics|stdlib全指標、candidate/selection/decisions重新實作|verification.json PASS84回合/10080步|
|中途失敗可覆寫、assert可關閉|exclusiveattempt/trace x模式、explicitrequire|6 adversarial tests在normal與-O模式PASS|
|freeze只是紀錄，執行重建defaults|使用resolved frozen config，來源snapshots保存|source/calibration/chronology/plantstep auditPASS|
|候選4/18/3不等、PID資訊基準弱|新版本各3候選/PID+FF，固定nominal資訊契約|36calepisodes全保存，48正式不重調|
|舊holdout已開過|新seeds/schedules/指定plantvariants，新目錄|新合成重複不冒稱獨立實體設備|
|資料/文稿籠統稱PID未評估|當前文件區分假設模型已評估、實體未評估|中文/IEEE/presentation/currentHTML來源及builder同步|

剩餘：7步strictresidual拒絕仍低於每回合5%門檻，後續不得因本輪測試再調threshold。改善比較假設H-CTRL-02/03均不支持，不另調到勝出。Office逐頁render缺runtime；實機量測缺設備/資料。
