import os
import re
import yaml
import hashlib
import json
from pathlib import Path
from datetime import datetime

# ─── 路徑設定 ──────────────────────────────────────────────
BASE_DIR = Path("/opt/Shrimp-LMM-Agent-Rag/Agent_Server/knowledge-base")
WIKI_DIR = BASE_DIR / "wiki"
RAW_DIR = BASE_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"

# ─── 工具函式 ──────────────────────────────────────────────
def get_all_md_files(directory):
    return list(directory.rglob("*.md"))

def parse_md(file_path):
    content = file_path.read_text(encoding="utf-8")
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if fm_match:
        try:
            return yaml.safe_load(fm_match.group(1)), fm_match.group(2)
        except:
            return None, content
    return None, content

def calculate_sha256(file_path):
    if not file_path.exists(): return None
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def jaccard_similarity(str1, str2):
    s1, s2 = set(str1.lower()), set(str2.lower())
    return len(s1 & s2) / len(s1 | s2) if len(s1 | s2) > 0 else 0

# ─── 核心 Lint 邏輯 ────────────────────────────────────────
class WikiLint:
    def __init__(self):
        self.files = get_all_md_files(WIKI_DIR)
        self.reports = []
        self.wikilinks_found = [] # (source_file, target_name)

    def run_checks(self):
        self.check_1_frontmatter()
        self.check_2_and_9_wikilinks()
        self.check_3_index_consistency()
        self.check_4_stub_pages()
        self.check_5_duplicate_names()
        self.check_6_sha_integrity()
        self.check_7_stale_pages()
        self.check_8_cross_lang_overlap()
        self.write_report()

    def check_1_frontmatter(self):
        errors = []
        for f in self.files:
            fm, _ = parse_md(f)
            if not fm or 'type' not in fm or 'date' not in fm:
                errors.append(f"- {f.relative_to(WIKI_DIR)}")
        if errors: self.reports.append("### 1. YAML Frontmatter 合法性錯誤\n" + "\n".join(errors))

    def check_2_and_9_wikilinks(self):
        broken = []
        format_err = []
        all_slugs = [f.stem for f in self.files]
        
        for f in self.files:
            _, body = parse_md(f)
            links = re.findall(r'\[\[(.*?)\]\]', body)
            for link in links:
                target = link.split('|')[0]
                self.wikilinks_found.append((f, target))
                if target not in all_slugs:
                    broken.append(f"- {f.name} -> [[{target}]] (不存在)")
                if not re.match(r'^[a-z0-9\-]+$', target) and not any('\u4e00' <= c <= '\u9fff' for c in target):
                    format_err.append(f"- {f.name}: [[{target}]] (格式不規範)")

        if broken: self.reports.append("### 2. Broken Wikilinks\n" + "\n".join(broken))
        if format_err: self.reports.append("### 9. Wikilink 格式規範建議\n" + "\n".join(format_err))

    def check_3_index_consistency(self):
        index_file = WIKI_DIR / "index.md"
        if not index_file.exists(): return
        _, body = parse_md(index_file)
        links = re.findall(r'\[\[(.*?)\]\]', body)
        missing = [f"- [[{l}]]" for l in links if not (WIKI_DIR.rglob(f"{l}.md"))]
        if missing: self.reports.append("### 3. Index 一致性錯誤 (索引指向不存在文件)\n" + "\n".join(missing))

    def check_4_stub_pages(self):
        stubs = []
        for f in self.files:
            if "templates" in str(f): continue
            _, body = parse_md(f)
            if len(body.strip()) < 100:
                stubs.append(f"- {f.name} ({len(body.strip())} 字)")
        if stubs: self.reports.append("### 4. Stub 頁面 (內容過少)\n" + "\n".join(stubs))

    def check_5_duplicate_names(self):
        dups = []
        slugs = [f.stem for f in self.files if "concepts" in str(f)]
        for i in range(len(slugs)):
            for j in range(i + 1, len(slugs)):
                sim = jaccard_similarity(slugs[i], slugs[j])
                if sim > 0.7:
                    dups.append(f"- {slugs[i]} <-> {slugs[j]} (相似度: {sim:.2f})")
        if dups: self.reports.append("### 5. 近重複概念名稱\n" + "\n".join(dups))

    def check_6_sha_integrity(self):
        sha_err = []
        for f in self.files:
            fm, _ = parse_md(f)
            if fm and fm.get('type') == 'source' and fm.get('raw_file'):
                raw_path = RAW_DIR / fm['raw_file'].replace('raw/', '')
                if not raw_path.exists():
                    sha_err.append(f"- {f.name}: 找不到原始檔 {fm['raw_file']}")
                    continue
                current_sha = calculate_sha256(raw_path)
                if current_sha != fm.get('raw_sha256'):
                    sha_err.append(f"- ⚠ **SOURCE MODIFIED**: {f.name} (SHA 不符)")
        if sha_err: self.reports.append("### 6. SHA-256 完整性檢查\n" + "\n".join(sha_err))

    def check_7_stale_pages(self):
        stale = []
        volatility_map = {"high": 90, "medium": 180, "low": 365}
        for f in self.files:
            fm, _ = parse_md(f)
            if fm and fm.get('type') == 'concept' and fm.get('updated'):
                days_limit = volatility_map.get(fm.get('domain_volatility', 'medium'), 180)
                last_update = datetime.strptime(str(fm['updated']), '%Y-%m-%d')
                delta = (datetime.now() - last_update).days
                if delta > days_limit:
                    stale.append(f"- {f.name} (已過期 {delta} 天)")
        if stale: self.reports.append("### 7. Stale 頁面 (超過時效閾值)\n" + "\n".join(stale))

    def check_8_cross_lang_overlap(self):
        overlaps = []
        aliases_map = {}
        for f in self.files:
            fm, _ = parse_md(f)
            if fm and fm.get('type') == 'concept' and fm.get('aliases'):
                for alias in fm['aliases']:
                    if alias in aliases_map:
                        overlaps.append(f"- 別名衝突: '{alias}' 同時存在於 {f.name} 與 {aliases_map[alias]}")
                    aliases_map[alias] = f.name
        if overlaps: self.reports.append("### 8. 跨語言/別名重複檢測\n" + "\n".join(overlaps))

    def write_report(self):
        report_name = f"lint-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path = OUTPUT_DIR / report_name
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        header = "---\ntype: system-lint-report\ngraph-excluded: true\n---\n\n# Wiki Lint Report\n\n"
        content = header + "\n\n".join(self.reports) if self.reports else header + "🎉 所有檢查通過！"
        report_path.write_text(content, encoding="utf-8")
        print(f"Report written to {report_path}")

if __name__ == "__main__":
    WikiLint().run_checks()