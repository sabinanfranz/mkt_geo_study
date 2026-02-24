"""Audit seeded step content for code block readability wrappers.

Usage:
  python scripts/audit_code_blocks.py
  python scripts/audit_code_blocks.py --db-path data/geo_mentor.db
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


PRE_OPEN_RE = re.compile(r"<pre(?:\s[^>]*)?>", re.IGNORECASE)


@dataclass(frozen=True)
class PreBlockIssue:
    step_id: int
    module_id: int
    title: str
    field: str
    snippet: str


def classify_pre_block(source: str, pre_start: int) -> str:
    context = source[max(0, pre_start - 320) : pre_start].lower()
    if "code-example" in context:
        return "code_example"
    if "log-example" in context:
        return "log_example"
    if "browser-body" in context:
        return "browser_pre"
    if "diagram-box" in context:
        return "diagram_pre"
    return "plain_pre"


def audit(db_path: Path) -> tuple[Counter, list[PreBlockIssue], int]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, module_id, title, content_md, extension_md FROM steps"
        ).fetchall()
    finally:
        conn.close()

    counts: Counter[str] = Counter()
    plain_issues: list[PreBlockIssue] = []
    total_pre_blocks = 0

    for row in rows:
        step_id = int(row["id"])
        module_id = int(row["module_id"])
        title = str(row["title"])

        for field in ("content_md", "extension_md"):
            raw = row[field]
            if not raw:
                continue
            source = str(raw)
            for match in PRE_OPEN_RE.finditer(source):
                total_pre_blocks += 1
                category = classify_pre_block(source, match.start())
                counts[category] += 1
                if category == "plain_pre":
                    start = max(0, match.start() - 120)
                    end = min(len(source), match.end() + 220)
                    snippet = source[start:end].replace("\n", " ")
                    plain_issues.append(
                        PreBlockIssue(
                            step_id=step_id,
                            module_id=module_id,
                            title=title,
                            field=field,
                            snippet=snippet.strip(),
                        )
                    )

    return counts, plain_issues, total_pre_blocks


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit <pre> block wrappers")
    parser.add_argument(
        "--db-path",
        default="data/geo_mentor.db",
        help="SQLite DB path (default: data/geo_mentor.db)",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"[FAIL] DB not found: {db_path}")
        return 2

    counts, plain_issues, total_pre = audit(db_path)

    print(f"DB: {db_path}")
    print(f"Total <pre> blocks: {total_pre}")
    for key in ("code_example", "log_example", "browser_pre", "diagram_pre", "plain_pre"):
        print(f"- {key}: {counts.get(key, 0)}")

    if plain_issues:
        print("\n[FAIL] plain <pre> blocks detected (missing readability wrapper):")
        for issue in plain_issues[:20]:
            print(
                f"- step={issue.step_id} module={issue.module_id} field={issue.field} "
                f"title={issue.title}"
            )
            print(f"  snippet: {issue.snippet[:220]}")
        if len(plain_issues) > 20:
            print(f"... and {len(plain_issues) - 20} more")
        return 1

    print("\n[OK] All <pre> blocks are wrapped with approved readability contexts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
