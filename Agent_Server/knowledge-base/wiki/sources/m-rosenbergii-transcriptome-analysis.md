---
title: 淡水長臂大蝦之轉錄體組裝與多維體資料分析
slug: m-rosenbergii-transcriptome-analysis
type: source
author: 高寘昕
date: 2022-06-01
raw_sha256: 0fa80b0911938e443837d0aa3ab107802c33e67cf58eb06062bfcce6796c083f
source_url: https://doi.org/10.6342/NTU202200893
possibly_outdated: false
tags: [淡水長臂大蝦, 轉錄體, 多維體分析, 抗菌肽, 甲殼類高血糖素]
---

# 淡水長臂大蝦之轉錄體組裝與多維體資料分析

## Summary
本研究為國立臺灣大學碩士論文，旨在建構淡水長臂大蝦（*Macrobrachium rosenbergii*）的完整轉錄基因體（Transcriptome），以彌補該物種缺乏完整基因體資料的不足，為智慧育種與功能研究提供基礎。研究整合了 20 筆轉錄體資料（涵蓋不同生長階段及感染 MrNV、哈維弧菌、白點症病毒之個體），透過 de novo assembly 組裝出約 20.9 萬條轉錄序列，BUSCO 完整度達 96.5%。此外，研究鑑別出 232 筆潛在抗菌肽（AMPs）序列，並分析了甲殼類高血糖素（CHH）家族的數量與多樣性，發現其少於對蝦科物種。最後，研究成果被整合至 MOLAS 線上資料庫中。

## Key Concepts
- [[transcriptome]]: 透過 RNA-seq 組裝而成的轉錄基因體，用於分析基因表達。
- [[antimicrobial-peptides]]: 鑑別出 232 筆潛在 AMPs，包含 crustin, Histone H2A 等。
- [[crustacean-hyperglycemic-hormone]]: 分析 CHH 家族，發現長臂蝦科的多樣性低於對蝦科。
- [[multi-omics]]: 整合基因體、轉錄體、蛋白質體之分析方法。
- [[phylogeny]]: 分析淡水長臂大蝦與日本沼蝦的共同祖先約在 94 百萬年前。

## Detailed Notes

### 1. 轉錄體組裝結果
- **資料來源**：整合 20 筆 SRA 轉錄資料。
- **組裝規模**：初步 26.3 萬條 $\rightarrow$ 去重後 20.9 萬條。
- **完整度**：BUSCO (arthopoda_odb10) 達 96.5%。
- **功能註解**：
    - 蛋白質預測：154,901 筆。
    - 訊號肽：6,325 條。
    - 穿膜蛋白：11,944 條。
    - KEGG 路徑：424 筆。

### 2. 抗菌肽 (AMPs) 鑑別
- 使用 AI4AMP 預測平台 $\rightarrow$ 7,913 筆結果。
- 比對 InverPep 資料庫 $\rightarrow$ 13 筆已知序列（如 crustin, MrH4）。
- 結合訊號肽篩選 $\rightarrow$ 232 筆潛在 AMPs。

### 3. 比較基因體學分析
- **物種對比**：與白蝦、草蝦、日本對蝦、中國對蝦（對蝦科）及日本沼蝦（長臂蝦科）比較。
- **CHH 家族**：淡水長臂大蝦的 CHH 數量與多樣性顯著低於對蝦科物種。
- **分化時間**：淡水長臂大蝦與日本沼蝦約 94 Ma 分化。

### 4. MOLAS 資料庫
- 建構 Multi-Omics online Analysis System (MOLAS)，提供圖像化線上分析環境，包含各組織 RNA 序列。

## Contradictions
(無明顯矛盾)

## Sources
- [[m-rosenbergii-transcriptome-analysis]]
