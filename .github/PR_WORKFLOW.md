# PR Workflow for This Repository

每次需求都以 PR 方式處理，避免直接在 main 上修改。

## 基本流程

1. 先從 main 建立一個獨立分支。
2. 在分支上完成需求與測試。
3. 執行必要驗證，確認結果可重現。
4. 將分支推到遠端，建立 PR。
5. 由另一個人或另一個帳號進行 review。
6. 根據 review 意見修正後，再合併到 main。
7. 合併後刪除分支，完成流程。

## 建議的分支命名

- `task/<short-description>`：一般功能或實驗改動
- `fix/<short-description>`：錯誤修正
- `review/<short-description>`：專門給 review 用的分支

## 建議的 PR 標題

- `[PR] <簡短任務描述>`

## PR 內容應包含

- 本次任務目標
- 變更內容摘要
- 驗證結果與測試命令
- 是否需要 reviewer 關注的重點

## Reviewer 的角色

- 檢查邏輯是否正確
- 檢查是否有風險或邊界情況未處理
- 確認測試是否足夠
- 確認這次變更是否與描述一致

## 完成標準
- 變更已實作
- 測試或驗證已完成
- PR 已建立且內容清楚
- 已收到 review 並處理完回饋
- 最終已合併到 main
