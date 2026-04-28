---
name: router-engine
description: 判斷本次操作是 ingest / query / lint / reflect
---

# 🧠 職責

決定 pipeline

---

# 🔄 分流規則

## CASE 1 - 有檔案
→ ingest-engine

---

## CASE 2 - 純問題
→ query-engine

---

## CASE 3 - lint trigger
→ lint-guardian

---

## CASE 4 - reflect trigger
→ reflect-engine

---

# 🧠 原則

> router = system brain entry point