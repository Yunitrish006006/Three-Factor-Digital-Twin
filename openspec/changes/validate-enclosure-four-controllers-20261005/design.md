# Design

CTRL-201/RQ-CTRL-01：独立v2 module、shared wrapper/ZOH predictor，無 case-specific 分支。CTRL-202/H-CTRL-02/03：固定 allocation 處理單風扇 reference、三候選校準後freeze。EVD-201/H-CTRL-01：resolved config直接執行、snapshot保存、exclusive marker/trace 防覆寫；獨立validator從stdlib CSV及方程重算與篡改測試。SYN-201：v1歷史summary和v2新summary分開，同步builders/outputs/HTML。

資料流 observation->controller->protection->plant->CSV->independent audit->reports。nonfinite observation拒絕；numeric failure/deadline fallback共用限制；soft thermal不是安全保證。Office缺runtime顯式pending。E15不重跑，無實體致動。
