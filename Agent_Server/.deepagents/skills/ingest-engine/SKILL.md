---
name: ingest-engine
description: 將 raw/ 來源轉換為 wiki 知識圖譜
---

# 🧠 職責

raw → wiki graph

---

# 🔄 主流程（11 steps）

## STEP 1 - 讀取來源
只讀 raw/

---

## STEP 2 - SHA-256
計算來源 hash

---

## STEP 3 - （必要時）與使用者確認

---

## STEP 4 - slug 生成

---

## STEP 5 - 建立 source

wiki/sources/<slug>.md


---

## STEP 6 - concept mapping（核心）

- slug normalize
- aliases check
- existing concept merge

---

## STEP 7 - concept 更新

- 更新 Definition
- 更新 Evolution Log
- 更新 source_count

---

## STEP 8 - entity 更新

同 concept 邏輯

---

## STEP 9 - index 更新

---

## STEP 10 - QUESTIONS 檢查

---

## STEP 11 - log 寫入

---

# 🧠 personal 規則

若來源為 personal：

- 不寫 summary
- 不計 confidence
- 寫入 My Position
- 標記 subjective

---

# 🧠 原則

> ingest = knowledge expansion engine