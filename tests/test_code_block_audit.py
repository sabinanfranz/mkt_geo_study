"""Seeded content audit for code block wrapper consistency."""

from __future__ import annotations

import re
from collections import Counter

from apps.api.database import get_db, init_db
from apps.api.seed import seed


PRE_OPEN_RE = re.compile(r"<pre(?:\s[^>]*)?>", re.IGNORECASE)


def _classify_pre_block(source: str, pre_start: int) -> str:
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


def test_seed_has_no_plain_pre_blocks():
    init_db()
    seed(run_migrations=False)

    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, module_id, title, content_md, extension_md FROM steps"
        ).fetchall()
    finally:
        conn.close()

    counts: Counter[str] = Counter()
    plain_blocks: list[tuple[int, int, str, str]] = []

    for row in rows:
        step_id = row["id"]
        module_id = row["module_id"]
        title = row["title"]
        for field in ("content_md", "extension_md"):
            source = row[field] or ""
            for match in PRE_OPEN_RE.finditer(source):
                category = _classify_pre_block(source, match.start())
                counts[category] += 1
                if category == "plain_pre":
                    plain_blocks.append((step_id, module_id, title, field))

    assert counts["code_example"] > 0, "Expected at least one .code-example pre block"
    assert counts["log_example"] > 0, "Expected at least one .log-example pre block"
    assert not plain_blocks, (
        "Found plain <pre> blocks without readability wrapper: "
        + ", ".join(
            f"step={sid}/module={mid}/field={field}/title={title}"
            for sid, mid, title, field in plain_blocks[:10]
        )
    )
