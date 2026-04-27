# AGENTS.md (v3.0 - 實體路徑與問題驅動強化版)

## 1. 專案概要 (Project Overview)
- **專案名稱**: Shrimp-LMM-Agent-Rag
- **核心邏輯**: **問題導向之全庫檢索 (Question-Driven Knowledge Retrieval)**。
- **原則**: Agent 嚴禁使用相對路徑，必須將實體目錄視為唯一事實。遵循「先全庫掃描、後精準執行、完工必驗」的硬性規章。

## 2. 核心決策流 (The Core Loop) —— **動態路徑與強制檢索**

### 階段一：問題解構與全局檢索 (Global Search & Path Alignment)
- **行動**：
    1. 讀取本文件 `AGENTS.md` 確立操作邊界。
    2. **強制執行絕對路徑掃描**：禁止使用內建 `ls` 工具。必須調用 `run_shell` 執行：
       `ls -R /opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base/`
- **目的**：獲取知識庫的「實時快照」，解決內建工具因路徑偏移導致回傳空結果 `[]` 的問題。
- **路徑指引**：
    - 涉及行為分析 $\rightarrow$ 檢索 `raw/observations/`。
    - 涉及文獻研讀 $\rightarrow$ 檢索 `raw/articles/` (必須調用 `read_pdf_text`)。
    - 涉及操作紀錄 $\rightarrow$ 檢索 `wiki/log.md`。

### 階段二：任務映射與動作執行 (Task Mapping & Action)
根據階段一掃描到的**實體檔案列表**，自動切換至對應動作：
- **[情境 A：數據處理]**：若偵測到新的 `.json` $\rightarrow$ 執行數據分析並更新 `wiki/concepts/`。
- **[情境 B：知識轉化]**：發現 PDF $\rightarrow$ 執行 `read_pdf_text` $\rightarrow$ 計算 SHA-256 (使用 `run_shell`) $\rightarrow$ 寫入 `wiki/sources/`。
- **[情境 C：路徑修復]**：若 `ls` 回傳失敗，Agent 必須回報 `/opt` 權限狀態，嚴禁回覆空白或靜默重試。

### 階段三：日誌同步與寫入驗證 (Live Logging & Verification)
- **行動**：
    1. 執行過程中任何關鍵動作（如計算雜湊、提取摘要）必須寫入 `wiki/log.md`。
    2. **寫入即驗證**：使用 `write_file` 後，必須立刻執行 `run_shell(command="ls -l [絕對路徑]")` 獲取檔案大小，證明寫入成功。

### 階段四：閉環驗證與標準校對 (Final Standards)
- **行動**：回對 `AGENTS.md` 檢查產出：
    - **事實對齊**：結論是否確實引用了 `raw/` 內的數據？
    - **術語標準**：專業術語是否符合 `中文 (English)` 格式？
    - **結構標準**：引用是否皆為 `[[wikilink-format]]`？

## 3. 實體路徑規範 (Path Standards)
- **根目錄 (Root)**: `/opt/Shrimp-LMM-Agent-Rag/Agent_Server/`
- **知識庫 (KB)**: `knowledge-base/`
- **強制規範**: 禁止操作上述路徑以外的檔案。