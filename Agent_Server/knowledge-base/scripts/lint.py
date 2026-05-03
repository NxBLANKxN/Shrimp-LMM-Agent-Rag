import os
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from itertools import combinations

BASE_DIR = Path(__file__).resolve().parent.parent
WIKI_ROOT = BASE_DIR / "wiki"
RAW_ROOT = BASE_DIR / "raw"
OUTPUT_DIR = WIKI_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_frontmatter_and_body(content):
    match = re.match(r"^---\n(.*?)\n---(.*)", content, re.DOTALL)
    if not match: return None, content
    fm_text = match.group(1)
    body = match.group(2).strip()
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                fm[key] = items
            else:
                fm[key] = val.strip("'\"")
    return fm, body

def get_bigrams(s):
    return set(s[i:i+2] for i in range(len(s)-1))

def jaccard_similarity(s1, s2):
    b1, b2 = get_bigrams(s1), get_bigrams(s2)
    if not b1 and not b2: return 1.0
    if not b1 or not b2: return 0.0
    return len(b1.intersection(b2)) / len(b1.union(b2))

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return None

def run_lint():
    report_lines = []
    report_lines.append(f"---")
    report_lines.append(f"type: lint-report")
    report_lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
    report_lines.append(f"graph-excluded: true")
    report_lines.append(f"---")
    report_lines.append(f"# 系統健康檢查報告 ({datetime.now().strftime('%Y-%m-%d')})")
    report_lines.append("")

    all_md_files = list(WIKI_ROOT.rglob("*.md"))
    check_files = [f for f in all_md_files if "templates" not in f.parts and "outputs" not in f.parts]
    all_slugs = set(f.stem for f in all_md_files)
    
    concepts = []
    concept_aliases = {}
    source_urls = {}
    
    errors = {
        "1. YAML frontmatter 合法性": [],
        "2. Broken Wikilinks (斷鏈)": [],
        "3. Index 一致性": [],
        "4. Stub 頁面 (空殼頁面)": [],
        "5. 近重複概念名稱": [],
        "6. SHA-256 完整性": [],
        "7. Stale 頁面 (過期頁面)": [],
        "8. 跨語言重複": [],
        "9. Wikilink 格式規範": []
    }

    index_links = []
    index_file = WIKI_ROOT / "index.md"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        index_links = re.findall(r"\[\[(.*?)\]\]", content)
    
    for link in index_links:
        target = link.split("|")[0].split("#")[0].strip()
        if target not in all_slugs:
            errors["3. Index 一致性"].append(f"Index 參照了遺失的頁面: [[{target}]]")

    for fpath in check_files:
        rel_path = fpath.relative_to(WIKI_ROOT)
        content = fpath.read_text(encoding="utf-8")
        
        # 1. Frontmatter
        fm, body = extract_frontmatter_and_body(content)
        if fm is None:
            errors["1. YAML frontmatter 合法性"].append(f"{rel_path}: 缺少 frontmatter")
        else:
            if "type" not in fm:
                errors["1. YAML frontmatter 合法性"].append(f"{rel_path}: frontmatter 缺少 'type'")
            if not str(rel_path).startswith("log") and not str(rel_path).startswith("index") and not str(rel_path).startswith("overview") and not str(rel_path).startswith("QUESTIONS"):
                if "date" not in fm:
                    errors["1. YAML frontmatter 合法性"].append(f"{rel_path}: frontmatter 缺少 'date'")

        # 4. Stub Pages
        if len(body) < 100 and fm and fm.get("type") not in ["system-index", "system-log", "system-overview", "system-questions"]:
            errors["4. Stub 頁面 (空殼頁面)"].append(f"{rel_path}: 內文字數少於 100 字")
            
        # Extract Wikilinks
        links = re.findall(r"\[\[(.*?)\]\]", content)
        for link in links:
            target = link.split("|")[0].split("#")[0].strip()
            
            # 9. Wikilink Format
            if not re.match(r"^[a-z0-9-]+$", target) and "/" not in target:
                errors["9. Wikilink 格式規範"].append(f"{rel_path}: 無效的連結格式 [[{target}]]")
                
            # 2. Broken Wikilinks
            if target not in all_slugs and not (WIKI_ROOT / target).exists() and not target.startswith("wiki/"):
                errors["2. Broken Wikilinks (斷鏈)"].append(f"{rel_path}: 斷鏈 [[{target}]]")

        if fm:
            type_val = fm.get("type", "")
            
            # 6. SHA-256 Integrity
            if type_val in ["source", "personal-writing"]:
                raw_file = fm.get("raw_file", "")
                expected_sha = fm.get("raw_sha256", "")
                if raw_file and expected_sha:
                    raw_path = BASE_DIR / raw_file
                    if raw_path.exists():
                        actual_sha = compute_sha256(raw_path)
                        if actual_sha != expected_sha:
                            errors["6. SHA-256 完整性"].append(f"{rel_path}: ⚠ SOURCE MODIFIED (哈希值不匹配)")
                    else:
                        errors["6. SHA-256 完整性"].append(f"{rel_path}: 找不到原始檔案 {raw_file}")
                
                url = fm.get("source_url", "")
                if url:
                    if url in source_urls:
                        errors["8. 跨語言重複"].append(f"重複的 source_url 存在於 {rel_path} 與 {source_urls[url]}")
                    else:
                        source_urls[url] = rel_path
                        
            # 7. Stale Pages
            if type_val == "concept":
                date_str = fm.get("last_reviewed") or fm.get("updated") or fm.get("date")
                volatility = fm.get("domain_volatility", "medium")
                if date_str:
                    try:
                        d = datetime.strptime(date_str, "%Y-%m-%d")
                        days_passed = (datetime.now() - d).days
                        limit = 90 if volatility == "high" else (180 if volatility == "medium" else 365)
                        if days_passed > limit:
                            errors["7. Stale 頁面 (過期頁面)"].append(f"{rel_path}: 頁面已過期 (上次更新於 {days_passed} 天前，限制為 {limit} 天)")
                    except ValueError:
                        pass
                
                concepts.append(fpath.stem)
                aliases = fm.get("aliases", [])
                if isinstance(aliases, list):
                    for alias in aliases:
                        if alias in concept_aliases and concept_aliases[alias] != fpath.stem:
                            errors["8. 跨語言重複"].append(f"別名重疊: '{alias}' 存在於 {fpath.stem} 與 {concept_aliases[alias]}")
                        concept_aliases[alias] = fpath.stem

    # 5. Near-Duplicate Concepts
    for c1, c2 in combinations(concepts, 2):
        if jaccard_similarity(c1, c2) > 0.7:
            errors["5. 近重複概念名稱"].append(f"高相似度 (>0.7): [[{c1}]] 與 [[{c2}]]")

    # Generate Report
    for check_name, errs in errors.items():
        report_lines.append(f"## {check_name}")
        if not errs:
            report_lines.append("✅ 通過")
        else:
            for err in errs:
                report_lines.append(f"- {err}")
        report_lines.append("")

    report_content = "\n".join(report_lines)
    report_file = OUTPUT_DIR / f"lint-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report_content, encoding="utf-8")
    print(f"Lint complete. Report saved to {report_file}")

if __name__ == "__main__":
    run_lint()
