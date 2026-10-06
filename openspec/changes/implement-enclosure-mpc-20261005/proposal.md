# Proposal

教授提出 MPC 方向，但既有程式只有 PI 與靜態候選操作排序，尚無機箱有限 horizon 閉環控制比較。本 change 實作 CPU/GPU 熱模型、共用風扇動態及受限制 MPC，完成可重設假設模型的探索性比較。

影響為 exploratory claim-neutral：不採納成主論文確認成果、不變更 E15/E8 既有結論。新證據 ID 為 E-MPC-01（模擬可行性）與 E-MPC-02（預定模型失配及極端負載）。不執行硬體。

同步範圍：中文 thesis_draft_zh.md 與 build_thesis_docx.py、IEEE paper.tex/references.bib、build_thesis_pptx.py 與兩份 outlines、中文 DOCX/PDF、IEEE PDF、既有兩份 PPTX，以及新離線 HTML。主模型架構圖未改動；新增控制結果圖独立保存。
