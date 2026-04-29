# AGENTS.md

## 專案概述

智慧蝦隻養殖 AI 知識系統，專門處理使用者對於養殖有關的問題，例如水質管理、病害預防與治療、飼料優化、養殖環境控制，以及自動化監控系統的整合應用等，期望能協助養殖業者提升生產效率、降低風險，並促進永續養殖的發展。

## 專案架構

knowledge-base/                              # 知識庫根目錄
    ├── output/                              # 輸出檔案
    │   ├── lint.md                          # lint 報告
    │   └── query.md                         # 查詢結果
    ├── raw/                                 # 原始資料
    │   ├── articles/                        # 手動保存的文獻
    │   ├── audio/                           # 音訊
    │   ├── clippings/                       # 剪報
    │   ├── datasets/                        # 資料集
    │   ├── documents/                       # 文件
    │   ├── images/                          # 圖片
    │   ├── notes/                           # 筆記
    │   ├── observations/                    # 觀察
    │   ├── pdfs/                            # PDF 文件
    │   ├── personal/                        # 使用者自己寫的文章或筆記
    │   └── videos/                          # 影片
    ├── scripts/                             # 腳本
    │   ├── lint.py                          # wiki 健康檢查腳本
    │   └── qmd-reindex.sh                   # 重建 qmd 索引腳本
    └── wiki/                                # 知識庫核心資料
        ├── QUESTIONS.md                     # 知識庫中常被問到的問題
        ├── concepts/                        # 概念定義
        ├── entities/                        # 實體定義
        ├── index.md                         # 內容索引
        ├── log.md                           # 操作日誌
        ├── overview.md                      # 知識庫總覽
        ├── sources/                         # 每個來源的摘要
        ├── synthesis/                       # 跨來源合成分析
        └── templates/                       # 模板
            ├── concept-template.md          # 概念定義模板
            ├── entity-template.md           # 實體定義模板
            ├── personal-writing-template.md # 使用者個人寫作模板
            ├── source-template.md           # 來源摘要模板
            └── synthesis-template.md        # 跨來源合成模板
## 作業流程

**1. 使用者輸入 Query（問題）**
   - Agent 接收到問題後，判斷是否為「知識庫查詢」
   
**2. 檢查知識庫是否已有答案（Query-First）**
   - 使用工具
   - 查詢 `QUESTIONS.md` + `index.md`，看是否有現成的答案
   
**3. 知識庫有答案（Direct Hit）**
   - Agent 直接回傳找到的現有答案（無需重新生成）
   - 流程結束
   
**4. 知識庫無答案（Generation Required）**
   - Agent 知道目前沒有現成答案
   - 開始 RAG + 生成流程：
     1. 從 knowledge-base/raw/ 中檢索相關文件
     2. 根據檢索結果生成答案
     3. 返回答案給使用者
   
**5. 生成後續處理（Optional）**
   - Agent 可選擇將新生成的問題：
     - 加入 QUESTIONS.md 作為未來問題範例
     - 更新相關 concepts/entities 定義
     - 記錄到 log.md
     - 並依照 wiki 中的模板分別依序寫入各個對應的資料夾中
