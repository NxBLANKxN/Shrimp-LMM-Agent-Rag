---
name: query-engine
description: 從 wiki graph 中檢索 + 推理 + 生成答案
---

# 🧠 職責

wiki → reasoning → answer

---

# 🔄 流程

## STEP 1 - retrieval

搜尋：

- concepts/
- entities/
- sources/
- synthesis/

---

## STEP 2 - context build

建立知識上下文圖譜

---

## STEP 3 - reasoning

- cross-source inference
- contradiction detection
- synthesis

---

## STEP 4 - answer generation

markdown output

---

## STEP 5 - optional write-back

新知識 → ingest-engine

---

## STEP 6 - output record

outputs/query.md


---

# 🧠 原則

> query = knowledge synthesis engine