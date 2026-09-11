#!/usr/bin/env python3
"""Enable JATS and eLIBRARY XML outputs on existing content pages.

One-off script (idempotent):
  - RU articles (content/article/YYYY/MM/NN.md with doi, not 00.md):
    insert outputs=["HTML", "JATS"]
  - EN articles: keep outputs=["HTML", "DOI"] untouched (the bilingual JATS
    file is rendered by the Russian build only)
  - Issue term pages (content{,_en}/issue/YYYY-MM/_index.md):
    write outputs=["HTML", "Elibrary"] front matter (files are empty bundles)
"""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent

RU_OUTPUTS = 'outputs=["HTML", "JATS"]'
ISSUE_OUTPUTS = 'outputs=["HTML", "Elibrary"]'

ISSUE_RE = re.compile(r'^issue="([^"]+)"', re.MULTILINE)


def process_article(path: Path, is_en: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if is_en:
        return "skipped"
    if "outputs=" in text or 'doi="' not in text:
        return "skipped"
    new_text, n = re.subn(r'^(categories\s*=\s*"article")\s*$',
                          r'\1\n' + RU_OUTPUTS, text, count=1,
                          flags=re.MULTILINE)
    if n:
        path.write_text(new_text, encoding="utf-8")
        return "inserted"
    return "skipped"


ISSUE_INDEX_CONTENT = '+++\noutputs=["HTML", "Elibrary"]\n+++\n'


def process_issue_index(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("+++"):
        return "skipped"
    path.write_text(ISSUE_INDEX_CONTENT, encoding="utf-8")
    return "written"


def collect_issue_values() -> list:
    values = set()
    for pattern in ("content/article/*/*/*.md", "content_en/article/*/*/*.md"):
        for path in ROOT.glob(pattern):
            m = ISSUE_RE.search(path.read_text(encoding="utf-8"))
            if m:
                values.add(m.group(1))
    return sorted(values)


def main() -> None:
    stats = Counter()
    for is_en, pattern in ((False, "content/article/*/*/*.md"),
                           (True, "content_en/article/*/*/*.md")):
        for path in sorted(ROOT.glob(pattern)):
            if path.name == "00.md":
                continue
            stats[f"article {'EN' if is_en else 'RU'}: "
                  f"{process_article(path, is_en)}"] += 1

    for issue in collect_issue_values():
        for base in ("content", "content_en"):
            issue_dir = ROOT / base / "issue" / issue
            index = issue_dir / "_index.md"
            if index.exists():
                stats[f"issue {base}: {process_issue_index(index)}"] += 1
            else:
                issue_dir.mkdir(parents=True, exist_ok=True)
                index.write_text(ISSUE_INDEX_CONTENT, encoding="utf-8")
                stats[f"issue {base}: created"] += 1

    for key in sorted(stats):
        print(f"{key}: {stats[key]}")


if __name__ == "__main__":
    main()
