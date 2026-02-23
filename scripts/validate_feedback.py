"""Feedback quality validation script.

Run: python scripts/validate_feedback.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.database import get_db, init_db


def validate():
    init_db()
    conn = get_db()

    rows = conn.execute(
        "SELECT o.id, o.step_id, o.label, o.feedback_md, o.is_correct, "
        "LENGTH(o.feedback_md) AS flen, s.module_id, s.title AS step_title "
        "FROM options o JOIN steps s ON o.step_id = s.id "
        "ORDER BY o.id"
    ).fetchall()

    total = len(rows)
    issues = []

    for r in rows:
        flen = r["flen"]
        fb = r["feedback_md"]

        # AC-1: 40~100 chars
        if flen < 40:
            issues.append(f"[SHORT] opt {r['id']} step {r['step_id']} [{r['label']}] len={flen}")
        elif flen > 100:
            issues.append(f"[LONG]  opt {r['id']} step {r['step_id']} [{r['label']}] len={flen}")

        # AC-3: polite tone (Korean polite endings: 니다, 세요, 요)
        fb_stripped = fb.rstrip(". !?")
        if not any(fb_stripped.endswith(e) for e in ("니다", "세요", "어요", "아요")):
            issues.append(f"[TONE]  opt {r['id']} step {r['step_id']} [{r['label']}] no polite ending")

    # Summary
    lengths = [r["flen"] for r in rows]
    print(f"=== Feedback Quality Report ===")
    print(f"Total options: {total}")
    print(f"Avg length: {sum(lengths)/len(lengths):.0f} chars")
    print(f"Min: {min(lengths)}, Max: {max(lengths)}")
    print(f"In range (40-100): {sum(1 for l in lengths if 40 <= l <= 100)}/{total}")
    print(f"Issues found: {len(issues)}")
    for iss in issues:
        print(f"  {iss}")

    conn.close()
    return len(issues) == 0


if __name__ == "__main__":
    ok = validate()
    if ok:
        print("\nAll feedback passes quality check.")
    else:
        print("\nSome feedback needs improvement.")
