# AGENTS.md

## 🧠 System Identity

智慧蝦隻養殖 AI 知識系統

---

## 📦 Knowledge Structure

知識庫位置：knowledge-base/

系統包含三層：

### 1. raw/
- 人類提供的原始資料
- LLM 僅可讀取
- 不可修改

---

### 2. wiki/
- 系統核心知識庫
- LLM 可讀寫
- 包含：
  - concepts（概念）
  - entities（實體）
  - sources（來源）
  - synthesis（推理結果）
  - index（索引）
  - log（紀錄）

---

### 3. outputs/
- 系統輸出結果
- 包含查詢與分析報告

---

## 🔁 三種操作模式（核心行為）

---

## 🟢 INGEST（匯入模式）

觸發條件：
- 使用者上傳資料
- 或輸入 ingest / 攝入 / 處理這個

### 行為流程：

1. 讀取 raw 資料（只讀）
2. 判斷資料類型
3. 解析內容
4. 建立或更新 wiki/sources
5. 抽取概念與實體
6. 更新相關 concepts / entities
7. 更新 index
8. 記錄 log

---

### 規則：

- 概念必須統一名稱
- 已存在 concept → 更新，不重建
- 所有知識必須可追溯來源

---

## 🔵 QUERY（查詢模式）

觸發條件：
- 使用者提問
- 或 query / 根據知識庫

### 行為流程：

1. 搜尋 wiki 相關內容
2. 讀取前 5 個最相關項目
3. 整合內容
4. 產生答案

---

### 規則：

- 必須基於 wiki
- 必須引用來源
- 可跨 concept 推理
- 可回寫新知識（若有價值）

---

## 🟣 LINT（健康檢查）

觸發條件：
- lint / 檢查 / 健康

### 行為：

- 檢查孤立概念
- 檢查矛盾定義
- 檢查缺失連結
- 檢查過期內容

---

### 輸出：

寫入 outputs/lint.md

---

## 🟡 REFLECT（反思模式）

觸發條件：
- reflect / 綜合分析

### 行為：

- 分析跨概念關聯
- 找出知識缺口
- 找出矛盾
- 找出隱性模式

---

### 輸出：

寫入 wiki/synthesis/

---

## 📌 系統規則

- raw/ 永遠不可修改
- wiki/log.md 只能追加
- 所有知識必須可追溯
- 所有變更必須記錄

---

## 🌏 語言規則

- 預設繁體中文
- concept 使用英文 slug
- aliases 支援中英文

---

## 🧠 核心原則

本系統是一個：

> 可持續演進的知識圖譜系統（Living Knowledge System）