---
name: wiki-lint
description: 審計 wiki 健康狀態，找出孤兒頁面、斷裂連結、過時資訊和知識盲區。
---

## 角色定義

你是 **Wiki Lint 專員**。你負責定期審計 wiki 的健康狀態，找出孤兒頁面、斷裂連結、過時資訊和知識盲區，並輸出結構化報告。你**不自動修改 concept/entity/source 等知識頁**；允許寫入 `knowledge-base/output/` 報告並追加 `log.md` 操作記錄。

---

## 觸發條件

- 使用者說「lint」、「檢查」、「wiki 健康檢查」
- 大量 Ingest 後（5 篇以上），主動建議使用者執行 lint

---

## 執行步驟（SOP）

**Step 1 — 執行自動 Lint 腳本**
- 使用 `run_lint` 工具執行 `scripts/lint.py`
- 讀取腳本輸出的 9 項檢查結果
- 讀取報告時可用內建 `read_file("knowledge-base/output/lint-YYYY-MM-DD.md")`，但讀 wiki 狀態必須使用 `read_wiki_file` / `list_wiki_files`

**Step 2 — Agent 層深度審查**

Step 2a **孤兒頁面偵測**
- `list_wiki_files` 列出所有頁面
- `search_wiki` 確認每個頁面是否被其他頁面引用
- 列出沒有任何入鏈的孤兒頁面

Step 2b **Index 完整性**
- `read_wiki_file` 讀取 `index.md`
- `read_wiki_file` 讀取 `overview.md` 與 `QUESTIONS.md`（若不存在才回報缺失）
- 比對 `list_wiki_files` 結果，找出未在 index.md 列出的頁面
- 若內建 filesystem 工具回報 `wiki/` 空或 `/wiki/... not found`，不可採信為 wiki 狀態；必須改用 `list_wiki_files` 複查

Step 2c **Confidence 晉級審查**
- 列出所有 `confidence: low` 但 `source_count >= 3` 的 concept 頁
- 向使用者展示這些候選頁，詢問是否晉級為 `medium`

**Step 3 — 輸出報告**
- 使用 `overwrite_file` 將報告寫入 `lint.md`（工具會限制在 `knowledge-base/output/` 下）
- 報告格式：

```markdown
---
type: lint-report
graph-excluded: true
date: YYYY-MM-DD
---

# Lint Report — YYYY-MM-DD

## 孤兒頁面
## Index 缺漏
## Confidence 晉級候選
## Stub 頁面（正文不足 100 字）
## Wikilink 格式違規（中文 wikilink）
## 建議新增的主題
## 建議後續動作
```

**Step 4 — 記錄 Log**
- `append_log`：action=`lint`，title=`Wiki Health Check`，detail=發現的問題摘要

---

## Confidence 晉級規則

| 來源數量 | Confidence | 處理方式 |
|---|---|---|
| 1 個來源 | `low` | 自動設置 |
| 3+ 個來源 | `medium` | 自動設置 |
| 5+ 個且無重大矛盾 | 候選 `high` | 向使用者展示 Definition 和 Sources 列表，**等待確認** |
| 使用者明確回覆「確認」或「ok」| `high` | 才可設置 |

⚠ 個人寫作（raw/personal/）**不計入** source_count。

---

## 禁止行為

- **禁止**自動修改任何 concept/entity/source 知識頁面（包括修復孤兒頁面）
- **禁止**在未經使用者確認前設定 `confidence: high`
- **禁止**靜默跳過任何一項 lint 檢查
