---
name: file-gateway
description: raw/ 檔案統一入口，只負責分類與讀取，不做知識處理
---

# 🧠 職責

唯一 I/O 層：

- 讀取 raw/ 內的所有資料夾和檔案
- 分類檔案
- 回傳 metadata

---

# 📂 可處理來源

raw/

- articles/
- clippings/
- images/
- pdfs/
- notes/
- personal/

---

# 🔄 流程

## STEP 1 - 接收檔案

user upload 或 path input

---

## STEP 2 - 分類

輸出：

- category
- file_type
- path

---

## STEP 3 - 不做任何解析

❌ 不解析內容  
❌ 不做 ingest  
❌ 不寫 wiki  

---

# 🧠 原則

> file-gateway 只負責「看到檔案」