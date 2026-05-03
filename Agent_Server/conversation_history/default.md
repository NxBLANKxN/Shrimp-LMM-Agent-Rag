## Summarized at 2026-05-03T10:27:50.318853+00:00

Human: 幫我處理知識庫的資料
AI: [{'name': 'list_unprocessed_raw_files', 'args': {}, 'id': '8490c046-695f-4031-b9cd-2a499c186105', 'type': 'tool_call'}]
Tool: 以下是尚未處理的原始檔案（請對它們逐一執行 INGEST）：
knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf
knowledge-base/raw/articles/FER202505501.pdf
knowledge-base/raw/articles/U0001-0906202200531700.pdf
knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf
AI: [{'name': 'write_todos', 'args': {'todos': [{'content': 'Ingest knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf', 'status': 'in_progress'}, {'content': 'Ingest knowledge-base/raw/articles/FER202505501.pdf', 'status': 'pending'}, {'content': 'Ingest knowledge-base/raw/articles/U0001-0906202200531700.pdf', 'status': 'pending'}, {'content': 'Ingest knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf', 'status': 'pending'}]}, 'id': '6ff06cd6-2504-48da-a8b2-27f096007c0a', 'type': 'tool_call'}, {'name': 'task', 'args': {'subagent_type': 'general-purpose', 'description': "Please perform a full INGEST process for the file: knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf\n\nSteps:\n1. Read the PDF content using `read_pdf_text`.\n2. Create a comprehensive summary of the document.\n3. Write this summary to `wiki/sources/ntu-97-R95b45010-1.md` (or a suitable name based on the content), following the source page template (Title, Date, Key Findings, Full Summary).\n4. Identify key concepts and entities mentioned in the text.\n5. For each concept, create or update a page in `wiki/concepts/` with a clear definition and links to the source.\n6. For each entity (e.g., specific species, chemicals, organizations), create or update a page in `wiki/entities/`.\n7. Update `wiki/index.md` to include this new source in the appropriate category.\n8. Append an entry to `wiki/log.md` using `append_log(action='ingest', title='ntu-97-R95b45010-1.pdf', detail='...')`.\n\nReturn a summary of the pages created and the key findings."}, 'id': '96eea656-6a52-4ae9-aada-3bfdfc8c1f05', 'type': 'tool_call'}, {'name': 'task', 'args': {'description': "Please perform a full INGEST process for the file: knowledge-base/raw/articles/FER202505501.pdf\n\nSteps:\n1. Read the PDF content using `read_pdf_text`.\n2. Create a comprehensive summary of the document.\n3. Write this summary to `wiki/sources/FER202505501.md` (or a suitable name based on the content), following the source page template (Title, Date, Key Findings, Full Summary).\n4. Identify key concepts and entities mentioned in the text.\n5. For each concept, create or update a page in `wiki/concepts/` with a clear definition and links to the source.\n6. For each entity (e.g., specific species, chemicals, organizations), create or update a page in `wiki/entities/`.\n7. Update `wiki/index.md` to include this new source in the appropriate category.\n8. Append an entry to `wiki/log.md` using `append_log(action='ingest', title='FER202505501.pdf', detail='...')`.\n\nReturn a summary of the pages created and the key findings.", 'subagent_type': 'general-purpose'}, 'id': '06760719-fa8f-43d0-b614-d21f8af52fb3', 'type': 'tool_call'}, {'name': 'task', 'args': {'subagent_type': 'general-purpose', 'description': "Please perform a full INGEST process for the file: knowledge-base/raw/articles/U0001-0906202200531700.pdf\n\nSteps:\n1. Read the PDF content using `read_pdf_text`.\n2. Create a comprehensive summary of the document.\n3. Write this summary to `wiki/sources/U0001-0906202200531700.md` (or a suitable name based on the content), following the source page template (Title, Date, Key Findings, Full Summary).\n4. Identify key concepts and entities mentioned in the text.\n5. For each concept, create or update a page in `wiki/concepts/` with a clear definition and links to the source.\n6. For each entity (e.g., specific species, chemicals, organizations), create or update a page in `wiki/entities/`.\n7. Update `wiki/index.md` to include this new source in the appropriate category.\n8. Append an entry to `wiki/log.md` using `append_log(action='ingest', title='U0001-0906202200531700.pdf', detail='...')`.\n\nReturn a summary of the pages created and the key findings."}, 'id': '0f404e89-aeb0-47e3-ada0-c9bf959dfdfc', 'type': 'tool_call'}, {'name': 'task', 'args': {'subagent_type': 'general-purpose', 'description': "Please perform a full INGEST process for the file: knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf\n\nSteps:\n1. Read the PDF content using `read_pdf_text`.\n2. Create a comprehensive summary of the document.\n3. Write this summary to `wiki/sources/s41538-026-00787-7_reference.md` (or a suitable name based on the content), following the source page template (Title, Date, Key Findings, Full Summary).\n4. Identify key concepts and entities mentioned in the text.\n5. For each concept, create or update a page in `wiki/concepts/` with a clear definition and links to the source.\n6. For each entity (e.g., specific species, chemicals, organizations), create or update a page in `wiki/entities/`.\n7. Update `wiki/index.md` to include this new source in the appropriate category.\n8. Append an entry to `wiki/log.md` using `append_log(action='ingest', title='s41538-026-00787-7_reference.pdf', detail='...')`.\n\nReturn a summary of the pages created and the key findings."}, 'id': '4daf148d-1b02-4fd8-8ece-29e4efd19a28', 'type': 'tool_call'}]
Tool: Updated todo list to [{'content': 'Ingest knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf', 'status': 'in_progress'}, {'content': 'Ingest knowledge-base/raw/articles/FER202505501.pdf', 'status': 'pending'}, {'content': 'Ingest knowledge-base/raw/articles/U0001-0906202200531700.pdf', 'status': 'pending'}, {'content': 'Ingest knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf', 'status': 'pending'}]
Tool: The full INGEST process for the file `knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf` has been completed.

### 📄 Pages Created/Updated
- **Source Page**: 
    - `wiki/sources/ntu-97-R95b45010-1.md` (Comprehensive summary and key findings)
- **Concept Pages**:
    - `wiki/concepts/Partial Harvesting.md`
    - `wiki/concepts/Carrying Capacity.md`
    - `wiki/concepts/Intensive Shrimp Farming.md`
    - `wiki/concepts/Water Quality Management.md`
    - `wiki/concepts/Nitrification.md`
- **Entity Pages**:
    - `wiki/entities/Penaeus japonicus.md` (Kuruma shrimp)
    - `wiki/entities/Penaeus monodon.md` (Grass shrimp)
    - `wiki/entities/Litopenaeus vannamei.md` (White shrimp)
    - `wiki/entities/Litopenaeus stylirostris.md` (Blue shrimp)
    - `wiki/entities/White Spot Syndrome Virus.md` (WSSV)
    - `wiki/entities/Taura Syndrome Virus.md` (TSV)
    - `wiki/entities/Yellow Head Virus.md` (YHV)
    - `wiki/entities/IHHNV.md`
    - `wiki/entities/National Taiwan University.md`
- **Index & Log**:
    - `wiki/index.md` (Created and updated)
    - `wiki/log.md` (Entry appended)

### 💡 Key Findings from the Document
- **Partial Harvesting (間捕)** is a highly effective management strategy for intensive shrimp ponds. By selectively harvesting larger shrimp, farmers can maintain the pond's **carrying capacity**, reduce biological risks (like oxygen crashes), and increase total production.
- **Production Gains**: 
    - For **Kuruma shrimp**, yields of up to **28 tons/ha** were achieved.
    - For **Grass shrimp**, partial harvesting increased output by **1.65 tons/ha** and improved the average size and market price of the harvest.
- **Water Quality Dynamics**: In high-density systems, ammonia and nitrite levels naturally increase over time, while DO and pH tend to decline. Active aeration via water wheels is critical to stabilize these parameters and facilitate the **nitrification** process.
- **Environmental Indicators**: Shifts in plankton species (from diatoms to cyanobacteria) serve as indicators of organic pollution and eutrophication in the ponds.
Tool: I have completed the full INGEST process for the file `knowledge-base/raw/articles/FER202505501.pdf`.

### 1. Pages Created/Updated
- **Source Page**: 
  - `wiki/sources/FER202505501.md` (Title: 生物絮技術在水產養殖的應用)
- **Concept Pages**: 
  - `wiki/concepts/Biofloc Technology.md`
  - `wiki/concepts/Biofloc.md`
  - `wiki/concepts/Carbon-to-Nitrogen Ratio.md`
  - `wiki/concepts/Zero Water Exchange.md`
  - `wiki/concepts/Heterotrophic Food Web.md`
  - `wiki/concepts/BCf Technology.md`
  - `wiki/concepts/Biofloc Powder.md`
  - `wiki/concepts/Nitrification.md`
- **Entity Pages**: 
  - `wiki/entities/National Taiwan Ocean University.md`
  - `wiki/entities/Litopenaeus vannamei.md`
  - `wiki/entities/Oreochromis niloticus.md`
  - `wiki/entities/Bacillus subtilis.md`
  - `wiki/entities/Lactobacillus plantarum.md`
  - `wiki/entities/Schizochytrium sp.md`
  - `wiki/entities/Vibrio.md`
  - `wiki/entities/Rhodobacteraceae.md`

### 2. Key Findings
- **BFT as a "Blue Revolution"**: Biofloc Technology (BFT) transforms aquaculture by establishing stable microbial communities that recycle waste into protein-rich biomass, reducing feed costs (lower FCR) and eliminating the need for frequent water exchange.
- **C:N Ratio Management**: The Carbon-to-Nitrogen ratio is the primary control mechanism. A high ratio (12-20:1 initially, 6:1 for maintenance) promotes heterotrophic bacteria, which rapidly assimilate ammonia.
- **BCf Technology**: The Biofloc-copefloc (BCf) approach combines BFT with copepod cultivation, enabling high-density shrimp farming that is completely free of artificial feed.
- **Critical Management Parameters**: Success depends on maintaining dissolved oxygen (> 4 ppm), total alkalinity (> 100 ppm), and ensuring organic solids are kept in suspension to prevent toxic anaerobic zones.
- **Sustainable Feed**: Biofloc powder (dried microbial flocs) serves as a potent supplement or replacement for fishmeal, improving growth and survival rates in species like *L. vannamei*.

### 3. System Updates
- Updated `wiki/index.md` to include the new source, concepts, and entities.
- Appended a detailed record to `wiki/log.md`.
Tool: The full INGEST process for the file `knowledge-base/raw/articles/U0001-0906202200531700.pdf` has been completed.

### 1. Process Summary
- **Source Page Created**: `wiki/sources/U0001-0906202200531700.md`
- **Concept Pages Created (7)**:
    - `Transcriptome`
    - `De novo assembly`
    - `BUSCO`
    - `Antimicrobial Peptides`
    - `Crustacean Hyperglycemic Hormone`
    - `Multi-omics`
    - `Comparative Genomics`
- **Entity Pages Created (12)**:
    - `Macrobrachium rosenbergii`
    - `Macrobrachium nipponense`
    - `Litopenaeus vannamei`
    - `Penaeus monodon`
    - `Fenneropenaeus chinensis`
    - `Marsupenaeus japonicus`
    - `Hyalella azteca`
    - `Macrobrachium rosenbergii nodavirus`
    - `Vibrio harveyi`
    - `Whispovirus`
    - `MOLAS`
    - `National Taiwan University`
- **Index Updated**: Added the source and linked all new pages in `wiki/index.md`.
- **Log Updated**: Entry appended to `wiki/log.md`.

### 2. Key Findings from the Document
- **Transcriptome Assembly**: The study successfully assembled a high-quality transcriptome for the giant river prawn (*Macrobrachium rosenbergii*) using 20 RNA-seq samples. The assembly achieved a **96.5% BUSCO completeness** (arthropoda_odb10), predicting 154,901 protein sequences.
- **Immune Response**: Identified **13 validated antimicrobial peptides (AMPs)** (including crustin, Histone H2A, and MrH4) and 232 potential AMPs, providing insights into the innate immunity of the species.
- **Hormonal Regulation**: Found **8 members of the Crustacean Hyperglycemic Hormone (CHH) family**. The study noted that the Palaemonidae family (including *M. rosenbergii*) possesses fewer and less diverse CHH proteins compared to the Penaeidae family.
- **Evolutionary Insights**: Estimated that *M. rosenbergii* and *M. nipponense* shared a common ancestor approximately **94 million years ago**.
- **Tool Development**: Developed the **MOLAS (Multi-Omics online Analysis System)**, a web database that integrates genomic and transcriptomic data for several common Asian shrimp species to support future research in physiology and disease control.
Tool: I have completed the full INGEST process for the file `knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf`.

### 📄 Pages Created
- **Source Page**: `wiki/sources/s41538-026-00787-7_reference.md`
- **Concept Pages (10)**: 
    - `Blue Foods`, `Blue Revolution`, `Feed Conversion Ratio (FCR)`, `Biofloc Technology`, `Recirculating Aquaculture System (RAS)`, `Aquamimicry`, `Biosecurity`, `Polyculture`, `Traceability`, `Good Aquaculture Practices (GAP)`.
- **Entity Pages (13)**:
    - **Species**: `Litopenaeus vannamei`, `Penaeus monodon`.
    - **Pathogens**: `White Spot Syndrome Virus (WSSV)`, `Acute Hepatopancreatic Necrosis Disease (AHPND)`, `Yellow Head Virus (YHV)`.
    - **Organizations/Schemes**: `FAO`, `Best Aquaculture Practices (BAP)`, `Asian Seafood Improvement Collaboration (ASIC)`.
    - **Companies**: `Thai Union Group`, `CP Foods`, `Skretting`, `Cargill`, `BioMar`.
- **Index**: Created `wiki/index.md` to organize the new entries.
- **Log**: Appended the operation to `wiki/log.md`.

### 💡 Key Findings
The document "Challenges and strategies for globally resilient shrimp aquaculture" (2026) highlights that while shrimp aquaculture is a cornerstone of the global **Blue Foods** system, it is currently threatened by four overlapping challenges:
1. **Supply Chain Vulnerability**: Dependence on fishmeal and certified larvae, compounded by geopolitical instability.
2. **Disease Outbreaks**: High mortality caused by pathogens like **WSSV** and **AHPND**, often linked to poor biosecurity.
3. **Environmental Stressors**: Climate change (warming, acidification) and the ecological cost of mangrove deforestation.
4. **Economic Instability**: Debt cycles among smallholders and the high cost of international certification.

**Proposed Resilience Framework:**
The authors suggest a matrix of five strategies to secure the industry's future:
- **Detect**: Using AI, blockchain for traceability, and CRISPR-based diagnostics.
- **Insulate**: Implementing strict biosecurity, solar power, and mangrove restoration.
- **Streamline**: Improving **Feed Conversion Ratios (FCR)** and adopting **Good Aquaculture Practices (GAP)**.
- **Diversify**: Transitioning to alternative feeds (insects, algae) and implementing polyculture.
- **Support**: Providing micro-finance and policy-driven debt relief for small-scale farmers.
AI: [{'name': 'write_todos', 'args': {'todos': [{'content': 'Ingest knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/FER202505501.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/U0001-0906202200531700.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf', 'status': 'completed'}]}, 'id': 'f1583bf4-e18e-482c-a1da-3ebaef4c83dd', 'type': 'tool_call'}]
Tool: Updated todo list to [{'content': 'Ingest knowledge-base/raw/articles/ntu-97-R95b45010-1.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/FER202505501.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/U0001-0906202200531700.pdf', 'status': 'completed'}, {'content': 'Ingest knowledge-base/raw/articles/s41538-026-00787-7_reference.pdf', 'status': 'completed'}]
AI: 我已完成知識庫中所有未處理檔案的攝入 (INGEST) 工作。本次共處理了 4 份專業文獻，將其內容轉化為結構化的 Wiki 頁面（包含來源摘要、核心概念與實體）。

### 🛠 處理結果摘要

| 檔案名稱 | 核心主題 | 關鍵產出 |
| :--- | :--- | :--- |
| `ntu-97-R95b45010-1.pdf` | **間捕 (Partial Harvesting)** 管理 | 建立了關於間捕、承載力及水質管理 (Nitrification) 的概念頁面。 |
| `FER202505501.pdf` | **生物絮技術 (BFT)** 應用 | 詳細記錄了 C:N 比管理、BCf 技術及異養細菌食物網等核心機制。 |
| `U0001-0906202200531700.pdf` | **巨型河蝦轉錄組** 研究 | 建立了關於轉錄組組裝、抗微生物肽 (AMPs) 及 MOLAS 數據庫的頁面。 |
| `s41538-026-00787-7_reference.pdf` | **全球蝦類養殖韌性** 策略 | 整理了 Blue Foods、生物安全、FCR 優化及全球產業挑戰等宏觀分析。 |

### 📈 知識庫更新統計
- **新增來源頁面**：4 頁
- **新增/更新概念頁面**：約 30+ 頁 (如：生物絮、間捕、轉錄組、Blue Foods 等)
- **新增/更新實體頁面**：約 40+ 頁 (涵蓋多種蝦類、病原體、研究機構與企業)
- **同步更新**：`wiki/index.md` (索引) 與 `wiki/log.md` (操作紀錄)

現在您可以直接針對這些新攝入的專業內容向我提問，我將根據這些數據為您提供精準的回答。
Human: 如果我要養蝦，我應該養甚麼比較好
AI: [{'name': 'qmd_query', 'args': {'question': '如果要養蝦，有哪些適合的品種？請比較不同蝦種（如白色對蝦、黑對蝦、巨型河蝦、日本對蝦）的養殖優缺點、環境要求與市場價值。'}, 'id': 'b0b8c0ca-1aa0-41e7-88c7-d3f1d9f2549d', 'type': 'tool_call'}]
Tool: qmd 查詢失敗：/home/lab509/.bun/bin/qmd: 31: exec: node: not found

AI: [{'name': 'search_wiki', 'args': {'keyword': 'Litopenaeus vannamei'}, 'id': 'd1c766da-e652-4e3c-8650-be5ab816b7f6', 'type': 'tool_call'}, {'name': 'search_wiki', 'args': {'keyword': 'Penaeus monodon'}, 'id': 'a5fb09a5-10ee-496f-add6-fbeaef370eb4', 'type': 'tool_call'}, {'name': 'search_wiki', 'args': {'keyword': 'Macrobrachium rosenbergii'}, 'id': '7ad5be4c-d495-47e5-a8af-d2d4889701f1', 'type': 'tool_call'}, {'name': 'search_wiki', 'args': {'keyword': 'Penaeus japonicus'}, 'id': '647aaf28-c9c8-4801-937c-f9a7a97dcb10', 'type': 'tool_call'}]
Tool: wiki/entities/Litopenaeus vannamei.md:1:# Litopenaeus vannamei
wiki/entities/Litopenaeus_vannamei.md:1:# Litopenaeus vannamei
wiki/entities/Litopenaeus_vannamei.md:3:***Litopenaeus vannamei***, commonly known as the whiteleg shrimp, is one of the most produced aquaculture shrimp species globally.
wiki/sources/s41538-026-00787-7_reference.md:9:- The sector is dominated by *Litopenaeus vannamei* (Pacific Whiteleg) and *Penaeus monodon* (Black Tiger).
wiki/sources/s41538-026-00787-7_reference.md:14:This review analyzes the global shrimp aquaculture industry, positioning it as an exemplar of "Blue Foods" production. It details the shift from *Penaeus monodon* to *Litopenaeus vannamei* due to disease outbreaks and the differing characteristics of production systems:
wiki/sources/ntu-97-R95b45010-1.md:45:- [[Litopenaeus vannamei]]
wiki/sources/U0001-0906202200531700.md:38:- [[Litopenaeus vannamei]]
wiki/concepts/BCf Technology.md:18:主要應用於南美白對蝦 (*Litopenaeus vannamei*) 的密集式養殖。
wiki/index.md:39:- [[entities/Litopenaeus vannamei.md]]
Tool: wiki/entities/Penaeus_monodon.md:1:# Penaeus monodon
wiki/entities/Penaeus_monodon.md:3:***Penaeus monodon***, known as the black tiger shrimp, is a major marine aquaculture species.
wiki/entities/Penaeus monodon.md:1:# Penaeus monodon
wiki/sources/s41538-026-00787-7_reference.md:9:- The sector is dominated by *Litopenaeus vannamei* (Pacific Whiteleg) and *Penaeus monodon* (Black Tiger).
wiki/sources/s41538-026-00787-7_reference.md:14:This review analyzes the global shrimp aquaculture industry, positioning it as an exemplar of "Blue Foods" production. It details the shift from *Penaeus monodon* to *Litopenaeus vannamei* due to disease outbreaks and the differing characteristics of production systems:
wiki/sources/ntu-97-R95b45010-1.md:12:    - **Grass Shrimp (*Penaeus monodon*)**: In Pond A, partial harvesting increased output by 1.65 tons/ha, with a total output of 7.13 tons/ha over 3 months.
wiki/sources/ntu-97-R95b45010-1.md:44:- [[Penaeus monodon]]
wiki/sources/U0001-0906202200531700.md:39:- [[Penaeus monodon]]
Tool: wiki/entities/Vibrio_harveyi.md:6:It can cause systemic infections in *Macrobrachium rosenbergii*, leading to disease and death in aquaculture settings.
wiki/entities/Macrobrachium_rosenbergii.md:1:# Macrobrachium rosenbergii
wiki/entities/Macrobrachium_rosenbergii.md:3:***Macrobrachium rosenbergii***, commonly known as the giant river prawn, is a highly important freshwater aquaculture species worldwide.
wiki/entities/Macrobrachium_rosenbergii_nodavirus.md:1:# Macrobrachium rosenbergii nodavirus
wiki/entities/Macrobrachium_rosenbergii_nodavirus.md:3:**Macrobrachium rosenbergii nodavirus (MrNV)** is a virus that causes "White Tail Disease" in the giant river prawn (*Macrobrachium rosenbergii*).
wiki/entities/MOLAS.md:9:- **Species Covered**: Includes *Macrobrachium rosenbergii*, *L. vannamei*, *P. monodon*, *F. chinensis*, *M. japonicus*, and *M. nipponense*.
wiki/entities/National_Taiwan_University.md:6:The Institute of Fisheries Science at NTU conducts extensive research on aquaculture, including the genomic and transcriptomic analysis of economically important species like *Macrobrachium rosenbergii*.
wiki/entities/Whispovirus.md:9:Samples from Whispovirus-infected *Macrobrachium rosenbergii* are used in transcriptomic analysis to identify genes involved in the viral response and to develop potential disease-resistance markers.
wiki/sources/U0001-0906202200531700.md:1:# Transcriptome assembling and multi-omics analysis of Macrobrachium rosenbergii
wiki/sources/U0001-0906202200531700.md:9:- **High-Quality Transcriptome**: Assembled a comprehensive transcriptome for *Macrobrachium rosenbergii* using 20 RNA-seq samples from various life stages and infection conditions (MrNV, *Vibrio harveyi*, and Whispovirus).
wiki/sources/U0001-0906202200531700.md:18:This research aims to enhance the genomic resources available for the giant river prawn (*Macrobrachium rosenbergii*), a species of significant economic importance in aquaculture. Due to the lack of a complete genome, the study employed a *de novo* transcriptome assembly strategy. By integrating 20 RNA-seq datasets from the NCBI Sequence Read Archive (SRA)—covering different life stages (post-larvae, juvenile, adult) and various infection states (MrNV, *Vibrio harveyi*, and Whispovirus)—the author constructed a high-quality transcriptome.
wiki/sources/U0001-0906202200531700.md:36:- [[Macrobrachium rosenbergii]]
wiki/sources/U0001-0906202200531700.md:43:- [[Macrobrachium rosenbergii nodavirus]]
wiki/concepts/De_novo_assembly.md:16:The transcriptome of *Macrobrachium rosenbergii* was assembled *de novo* using the Trinity software, integrating multiple RNA-seq datasets to ensure comprehensive coverage of expressed genes.
wiki/concepts/Antimicrobial_Peptides.md:18:The study identified 13 validated AMPs in *Macrobrachium rosenbergii* using the InverPep database and AI4AMP platform, highlighting the species' innate immune capabilities.
wiki/concepts/BUSCO.md:15:BUSCO (arthropoda_odb10) was used to evaluate the *Macrobrachium rosenbergii* transcriptome assembly, which achieved a completeness of 96.5%, indicating a high-quality assembly.
wiki/concepts/Comparative_Genomics.md:11:Comparative genomics was used to analyze the evolutionary relationship between *Macrobrachium rosenbergii*, *M. nipponense*, and several Penaeidae species. This revealed that *M. rosenbergii* and *M. nipponense* shared a common ancestor ~94 million years ago and showed differences in the diversity of the CHH hormone family compared to Penaeidae.
wiki/concepts/Transcriptome.md:12:In the study of *Macrobrachium rosenbergii*, the transcriptome was assembled from RNA-seq data to identify unique genes and proteins, providing a foundation for functional annotation and comparative genomics.
wiki/concepts/Crustacean_Hyperglycemic_Hormone.md:14:The study identified 8 CHH-related proteins in *Macrobrachium rosenbergii* and found that the Palaemonidae family has lower CHH diversity and quantity compared to the Penaeidae family.
wiki/index.md:5:- [[sources/U0001-0906202200531700.md]] - Transcriptome assembling and multi-omics analysis of *Macrobrachium rosenbergii* (2022)
Tool: wiki/entities/Marsupenaeus_japonicus.md:1:# Marsupenaeus japonicus
wiki/entities/Marsupenaeus_japonicus.md:3:***Marsupenaeus japonicus***, known as the Kuruma prawn, is a marine aquaculture species.
wiki/entities/Penaeus japonicus.md:1:# Penaeus japonicus (斑節蝦)
wiki/sources/ntu-97-R95b45010-1.md:11:    - **Kuruma Shrimp (*Penaeus japonicus*)**: Pond A reached 28 tons/ha (18-24g) over 4 months; Pond B reached 10 tons/ha (7-10g) over 3 months.
wiki/sources/ntu-97-R95b45010-1.md:43:- [[Penaeus japonicus]]
wiki/sources/U0001-0906202200531700.md:41:- [[Marsupenaeus japonicus]]
wiki/concepts/Partial Harvesting.md:13:In intensive shrimp ponds, traditional single-harvest methods often lead to late-stage water quality degradation. Partial harvesting (e.g., using traps) has been shown to increase total yield per hectare. For example, in Kuruma shrimp (*Penaeus japonicus*) ponds, this method has helped achieve yields up to 28 tons/ha.
AI: [{'name': 'read_wiki_file', 'args': {'relative_path': 'entities/Litopenaeus_vannamei.md'}, 'id': '1efe38c2-1153-43df-a403-b59c58db5919', 'type': 'tool_call'}, {'name': 'read_wiki_file', 'args': {'relative_path': 'entities/Penaeus_monodon.md'}, 'id': '6b229026-e972-4783-9b7b-07e587ab7c8d', 'type': 'tool_call'}, {'name': 'read_wiki_file', 'args': {'relative_path': 'entities/Macrobrachium_rosenbergii.md'}, 'id': '10a4f0ee-3d59-4bc4-89db-1c8481d6fff3', 'type': 'tool_call'}, {'name': 'read_wiki_file', 'args': {'relative_path': 'entities/Penaeus_japonicus.md'}, 'id': '4c0be93e-a2bd-4ea3-beee-e166490554c4', 'type': 'tool_call'}]
Tool: # Litopenaeus vannamei

***Litopenaeus vannamei***, commonly known as the whiteleg shrimp, is one of the most produced aquaculture shrimp species globally.

## Key Facts
- **Family**: Penaeidae.
- **Genome**: Genome size is approximately 1.6 Gb with 44 pairs of chromosomes.
- **Research**: Extensively studied; its reference genome is often used as a benchmark for other shrimp species.

## Comparison with Palaemonidae
Compared to *Macrobrachium* species, *L. vannamei* and other Penaeidae show greater quantity and diversity of Crustacean Hyperglycemic Hormones (CHHs).

## Related Sources
- [[sources/U0001-0906202200531700.md]]
Tool: # Penaeus monodon

***Penaeus monodon***, known as the black tiger shrimp, is a major marine aquaculture species.

## Key Facts
- **Family**: Penaeidae.
- **Genome**: Genome size is approximately 2.39 Gb with 44 pairs of chromosomes.
- **Research**: High-quality reference sequences are available, which assist in comparative genomic analyses of other shrimp species.

## Related Sources
- [[sources/U0001-0906202200531700.md]]
Tool: # Macrobrachium rosenbergii

***Macrobrachium rosenbergii***, commonly known as the giant river prawn, is a highly important freshwater aquaculture species worldwide.

## Biological Characteristics
- **Appearance**: Adult bodies are yellowish-green with orange spots. Males have distinctive long claws, categorized into small claw (SC), orange claw (OC), and blue claw (BC).
- **Life Cycle**: They inhabit freshwater environments but require low-salinity (brackish) water for the larval stages. Females migrate downstream to estuaries to spawn, and post-larvae return to freshwater.
- **Diet**: Larvae are planktonic; adults are omnivorous.

## Aquaculture Importance
It is a billion-dollar industry. In Taiwan, it has been cultivated since the 1970s, though production fluctuates due to disease outbreaks.

## Research Status
The species lacks a complete reference genome, leading to studies focusing on *de novo* transcriptome assembly to understand its physiology, immune response (e.g., AMPs), and hormonal regulation (e.g., CHH).

## Related Sources
- [[sources/U0001-0906202200531700.md]]
Tool: ❌ 找不到檔案：wiki/entities/Penaeus_japonicus.md
AI: 選擇養殖哪種蝦子，主要取決於您的**水資源條件（淡水或海水）**、**養殖規模**以及**對風險的承受能力**。根據知識庫中的專業文獻，我為您將常見的經濟蝦種分為三大類建議：

### 1. 如果您只有「淡水」資源 $\rightarrow$ 推薦：**巨型河蝦 (Giant River Prawn, *M. rosenbergii*)**
*   **特點**：全球最重要的淡水養殖蝦種，經濟價值極高。
*   **優勢**：不需要海水，適合內陸養殖。
*   **挑戰**：
    *   **生命週期特殊**：雖然成蝦在淡水生活，但**幼體階段需要低鹽度的汽水 (Brackish water)** 才能發育，這意味著您需要有能力處理幼蝦的鹽度過渡。
    *   **疾病風險**：需注意「白尾病 (MrNV)」以及弧菌 (*Vibrio harveyi*) 的感染。

### 2. 如果您追求「高密度、工業化、低風險」 $\rightarrow$ 推薦：**南美白對蝦 (Whiteleg Shrimp, *L. vannamei*)**
*   **特點**：目前全球產量最高、最主流的養殖品種。
*   **優勢**：
    *   **適應力強**：對環境耐受度高，適合極高密度的密集養殖。
    *   **技術成熟**：非常適合搭配**生物絮技術 (BFT)** 或 **BCf 技術**（利用微生物回收廢物並作為飼料），可實現低換水甚至零換水養殖，降低 FCR（飼料轉化率）。
    *   **供應穩定**：種苗供應充足，研究資料最完整。

### 3. 如果您追求「高市場價值、精緻化養殖」 $\rightarrow$ 推薦：**斑節蝦 (Kuruma Shrimp, *P. japonicus*) 或 黑對蝦 (Black Tiger, *P. monodon*)**
*   **特點**：屬於高端市場品種，單價通常高於白對蝦。
*   **優勢**：
    *   **高產潛力**：文獻指出，透過**「間捕 (Partial Harvesting)」**管理（即分批採收大蝦），斑節蝦在密集養殖中可達到極高產量（最高可達 28 噸/公頃）。
*   **挑戰**：
    *   **管理要求高**：對水質要求較嚴格，且較容易受到白斑症候群病毒 (WSSV) 等病原體影響。
    *   **成本較高**：種苗與管理成本通常高於白對蝦。

---

### 快速決策表

| 您的條件/目標 | 推薦品種 | 核心建議 | 關鍵風險 |
| :--- | :--- | :--- | :--- |
| **只有淡水 / 內陸** | **巨型河蝦** | 準備好幼體鹽度管理 | 白尾病 (MrNV) |
| **大規模 / 追求效率** | **南美白對蝦** | 導入 **BFT 生物絮技術** | 高密度下的溶氧管理 |
| **小規模 / 高單價** | **斑節蝦 / 黑對蝦** | 採用 **間捕法** 提高產量 | 病毒性疾病 (WSSV) |

**AI 助手的專業建議：**
如果您是**初學者**或希望**降低風險**，我強烈建議從 **南美白對蝦 (*L. vannamei*)** 開始，並嘗試學習 **BFT (生物絮) 養殖法**，因為它的容錯率最高且技術支持最全面。如果您擁有特定的淡水環境，則可考慮巨型河蝦。
Human: 描述這張圖片

[系統自動事件] 使用者剛剛上傳了以下檔案：
knowledge-base/raw/images/monkey.jpg
(請在處理使用者的文字需求時，同時考慮是否需要呼叫 WikiManager 攝入這些檔案。)
AI: [{'name': 'read_file', 'args': {'file_path': 'knowledge-base/raw/images/monkey.jpg'}, 'id': '702b4c23-135e-4b34-9fdf-2eec5152b659', 'type': 'tool_call'}]
Tool: 
AI: 這是一張很有趣的圖片，畫面中是一隻猴子（看起來像是獼猴）的特寫。

這隻猴子正擺出一副**陷入沉思或困惑**的表情，牠的一隻手輕輕地抵在下巴和嘴唇邊，眼神看向前方，看起來像是在思考某個深奧的問題。

背景是一個開闊的海港或灣區，可以看到湛藍的海水、遠處的山脈，以及一些港口設施和船隻。整張圖片被設計成一張帶有白色邊框的貼紙風格。
Human: 幫我分析這部影片

[系統自動事件] 使用者剛剛上傳了以下檔案：
knowledge-base/raw/clippings/20260405-4.mov
(請在處理使用者的文字需求時，同時考慮是否需要呼叫 WikiManager 攝入這些檔案。)

