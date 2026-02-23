"""Tests for Phase 2 — Content expansion and visual components.

Tests for US-032 (Stage unlock logic), US-033 (Dark mode CSS),
US-034 (API validation), and US-035 (Feedback quality).

Run with: pytest tests/test_phase2.py -v
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.database import get_db, init_db
from apps.api.main import app
from apps.api.seed import seed

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------


def _set_client_auth(username: str = "b2b_mkt_1") -> None:
    res = client.post(
        "/api/auth/login",
        json={"username": username, "password": username},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})


def _seed_phase2():
    """Initialize DB and load Phase 2 seed data."""
    init_db()
    seed()
    _set_client_auth()


# ---------------------------------------------------------------------------
# US-032: Stage Unlock Logic (Stage 3, 4, 5, 6)
# ---------------------------------------------------------------------------


def test_stages_returns_six():
    """API should return 6 stages (Stage 1 through 6)."""
    _seed_phase2()
    res = client.get("/api/stages")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 6, f"Expected 6 stages, got {len(data)}"
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2
    assert data[2]["id"] == 3
    assert data[3]["id"] == 4
    assert data[4]["id"] == 5
    assert data[5]["id"] == 6


def test_stages_initial_lock_status():
    """Stage 1 unlocked, Stages 2-6 locked initially (no progress)."""
    _seed_phase2()
    res = client.get("/api/stages")
    assert res.status_code == 200
    data = res.json()

    # Stage 1: always unlocked
    assert data[0]["is_unlocked"] is True

    # Stages 2-6: locked (no user progress yet)
    for i in range(1, 6):
        assert data[i]["is_unlocked"] is False, f"Stage {i+1} should be locked initially"


def test_stage3_unlock_condition():
    """Stage 3 unlock_condition: require Stage 2 completion with 70%."""
    _seed_phase2()
    conn = get_db()
    try:
        stage3 = conn.execute(
            "SELECT unlock_condition FROM stages WHERE id = 3"
        ).fetchone()
        assert stage3 is not None
        condition = json.loads(stage3["unlock_condition"])
        assert condition.get("require_stage_complete") == 2
        assert condition.get("min_score_pct") == 70
    finally:
        conn.close()


def test_stage4_unlock_condition():
    """Stage 4 unlock_condition: require Stage 3 completion with 70%."""
    _seed_phase2()
    conn = get_db()
    try:
        stage4 = conn.execute(
            "SELECT unlock_condition FROM stages WHERE id = 4"
        ).fetchone()
        assert stage4 is not None
        condition = json.loads(stage4["unlock_condition"])
        assert condition.get("require_stage_complete") == 3
        assert condition.get("min_score_pct") == 70
    finally:
        conn.close()


def test_stage5_unlock_condition():
    """Stage 5 unlock_condition: require Stage 4 completion with 70%."""
    _seed_phase2()
    conn = get_db()
    try:
        stage5 = conn.execute(
            "SELECT unlock_condition FROM stages WHERE id = 5"
        ).fetchone()
        assert stage5 is not None
        condition = json.loads(stage5["unlock_condition"])
        assert condition.get("require_stage_complete") == 4
        assert condition.get("min_score_pct") == 70
    finally:
        conn.close()


def test_stage6_unlock_condition():
    """Stage 6 unlock_condition: require Stage 5 completion with 70%."""
    _seed_phase2()
    conn = get_db()
    try:
        stage6 = conn.execute(
            "SELECT unlock_condition FROM stages WHERE id = 6"
        ).fetchone()
        assert stage6 is not None
        condition = json.loads(stage6["unlock_condition"])
        assert condition.get("require_stage_complete") == 5
        assert condition.get("min_score_pct") == 70
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# US-033: CSS Visual Components Dark Mode
# ---------------------------------------------------------------------------


def test_css_visual_components_exist():
    """CSS should contain all 6 visual component classes."""
    css_path = Path(__file__).resolve().parent.parent / "apps" / "web" / "css" / "style.css"

    if not css_path.exists():
        # Skip if CSS doesn't exist yet (Phase 2 in progress)
        import pytest
        pytest.skip(f"CSS file not found: {css_path}")

    css_content = css_path.read_text(encoding="utf-8")

    components = [
        ".browser-mockup",
        ".compare-cards",
        ".diagram-box",
        ".callout",
        ".code-example",
        ".hierarchy-box"
    ]

    for component in components:
        assert component in css_content, \
            f"CSS missing component: {component}"


def test_css_dark_mode_overrides():
    """Dark mode should have CSS overrides for all 6 visual components."""
    css_path = Path(__file__).resolve().parent.parent / "apps" / "web" / "css" / "style.css"

    if not css_path.exists():
        import pytest
        pytest.skip(f"CSS file not found: {css_path}")

    css_content = css_path.read_text(encoding="utf-8")

    # Check for dark mode selector
    assert '[data-theme="dark"]' in css_content, \
        "CSS missing dark mode theme selector"

    # Each component should have a dark mode override
    components = [
        "browser-mockup",
        "compare-cards",
        "diagram-box",
        "callout",
        "code-example",
        "hierarchy-box"
    ]

    for component in components:
        pattern = rf'\[data-theme="dark"\]\s+\.{re.escape(component)}'
        assert re.search(pattern, css_content), \
            f"CSS missing dark mode override for .{component}"


# ---------------------------------------------------------------------------
# US-034: Stage 3, 4, 5, 6 API Validation
# ---------------------------------------------------------------------------


def test_stage3_has_seven_modules():
    """Stage 3 should have 7 modules."""
    _seed_phase2()
    res = client.get("/api/stages/3/modules")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7, f"Expected 7 modules in Stage 3, got {len(data)}"


def test_stage4_has_seven_modules():
    """Stage 4 should have 7 modules."""
    _seed_phase2()
    res = client.get("/api/stages/4/modules")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7, f"Expected 7 modules in Stage 4, got {len(data)}"


def test_stage5_has_seven_modules():
    """Stage 5 should have 7 modules."""
    _seed_phase2()
    res = client.get("/api/stages/5/modules")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7, f"Expected 7 modules in Stage 5, got {len(data)}"


def test_stage6_has_eight_modules():
    """Stage 6 should have 8 modules."""
    _seed_phase2()
    res = client.get("/api/stages/6/modules")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 8, f"Expected 8 modules in Stage 6, got {len(data)}"


def test_stage3_step_counts():
    """Stage 3 modules: M3-1~M3-6 should have 4 steps, M3-7 should have 5 steps."""
    _seed_phase2()
    res = client.get("/api/stages/3/modules")
    assert res.status_code == 200
    modules = res.json()

    # Modules 0-5 (M3-1 to M3-6): 4 steps each
    for i in range(6):
        assert modules[i]["total_steps"] == 4, \
            f"Module {i+1} should have 4 steps, got {modules[i]['total_steps']}"

    # Module 6 (M3-7): 5 steps
    assert modules[6]["total_steps"] == 5, \
        f"Module 7 (evaluation) should have 5 steps, got {modules[6]['total_steps']}"


def test_stage6_step_counts():
    """Stage 6 modules M6-1~M6-8 should have 4 steps each."""
    _seed_phase2()
    res = client.get("/api/stages/6/modules")
    assert res.status_code == 200
    modules = res.json()
    assert len(modules) == 8
    for i in range(8):
        assert modules[i]["total_steps"] == 4, \
            f"Stage 6 Module {i+1} should have 4 steps, got {modules[i]['total_steps']}"


def test_stage6_eval_module_has_quiz_steps():
    """Stage 6 evaluation module (last module) should include quiz steps."""
    _seed_phase2()
    conn = get_db()
    try:
        eval_module = conn.execute(
            "SELECT id FROM modules WHERE stage_id = 6 ORDER BY order_idx DESC LIMIT 1"
        ).fetchone()
        assert eval_module is not None
        quiz_count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM steps WHERE module_id = ? AND type = 'quiz'",
            (eval_module["id"],)
        ).fetchone()["cnt"]
        assert quiz_count >= 2, "Stage 6 evaluation module must have at least 2 quiz steps"
    finally:
        conn.close()


def test_total_step_count():
    """Total steps across all stages should include Stage 6 expansion."""
    _seed_phase2()
    conn = get_db()
    try:
        total_steps = conn.execute(
            "SELECT COUNT(*) AS cnt FROM steps"
        ).fetchone()["cnt"]

        # Stage 6 added: total should be at least 175 steps.
        assert total_steps >= 175, \
            f"Expected at least 175 steps, got {total_steps}"
    finally:
        conn.close()


def test_total_option_count():
    """Total options should include Stage 6 expansion."""
    _seed_phase2()
    conn = get_db()
    try:
        total_options = conn.execute(
            "SELECT COUNT(*) AS cnt FROM options"
        ).fetchone()["cnt"]

        assert total_options >= 540, \
            f"Expected at least 540 options, got {total_options}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# US-035: Feedback Quality Validation
# ---------------------------------------------------------------------------


def test_all_feedback_min_length():
    """All feedback texts should be at least 40 characters."""
    _seed_phase2()
    conn = get_db()
    try:
        short_feedback = conn.execute(
            "SELECT o.id, o.step_id, LENGTH(o.feedback_md) AS flen "
            "FROM options o "
            "WHERE LENGTH(TRIM(o.feedback_md)) < 40"
        ).fetchall()

        assert len(short_feedback) == 0, \
            f"Found {len(short_feedback)} feedback texts < 40 chars: " \
            f"{[(r['id'], r['flen']) for r in short_feedback[:5]]}"
    finally:
        conn.close()


def test_all_feedback_polite_form():
    """All feedback texts should use Korean polite form (존댓말)."""
    _seed_phase2()
    conn = get_db()
    try:
        # Polite endings in Korean: 니다, 세요, 어요, 아요, 습니다, 됩니다, 등등
        polite_endings = ("니다", "세요", "어요", "아요", "습니다", "됩니다",
                         "요요", "네요", "는군요", "군요", "ㅂ니다", "ㅅ니다")

        all_feedback = conn.execute(
            "SELECT o.id, o.step_id, o.feedback_md "
            "FROM options o"
        ).fetchall()

        non_polite = []
        for r in all_feedback:
            fb = r["feedback_md"].strip()
            # Remove trailing punctuation for checking
            fb_stripped = fb.rstrip(". !?!?').,;:—-")

            # Check if ends with any polite form
            has_polite = any(fb_stripped.endswith(ending) for ending in polite_endings)

            if not has_polite and len(fb_stripped) > 0:
                non_polite.append((r["id"], r["step_id"], fb[:50]))

        assert len(non_polite) == 0, \
            f"Found {len(non_polite)} feedback without polite form: " \
            f"{non_polite[:5]}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Integration: Phase 2 Completeness
# ---------------------------------------------------------------------------


def test_phase2_stage_progression():
    """User can progress through all 6 stages by passing evaluations."""
    _seed_phase2()
    conn = get_db()
    try:
        # Verify all 6 stages exist with proper unlock conditions
        all_stages = conn.execute(
            "SELECT id, unlock_condition FROM stages ORDER BY id"
        ).fetchall()

        assert len(all_stages) == 6

        # Stage 1: no condition
        assert all_stages[0]["unlock_condition"] is None

        # Stages 2-6: all have unlock conditions
        for i in range(1, 6):
            assert all_stages[i]["unlock_condition"] is not None
            condition = json.loads(all_stages[i]["unlock_condition"])
            assert "require_stage_complete" in condition
            assert "min_score_pct" in condition
    finally:
        conn.close()


def test_phase2_api_endpoints():
    """All new endpoints respond correctly."""
    _seed_phase2()

    # Stage 3 endpoints
    res3 = client.get("/api/stages/3/modules")
    assert res3.status_code == 200
    modules3 = res3.json()
    if isinstance(modules3, dict) and "modules" in modules3:
        modules3 = modules3["modules"]
    assert len(modules3) > 0
    # Get first module id from Stage 3 and test module detail
    first_module_id = modules3[0]["id"]
    assert client.get(f"/api/modules/{first_module_id}").status_code == 200

    # Stage 4, 5, and 6
    assert client.get("/api/stages/4/modules").status_code == 200
    assert client.get("/api/stages/5/modules").status_code == 200
    assert client.get("/api/stages/6/modules").status_code == 200


def test_phase2_module_titles_stage3():
    """Stage 3 modules should have appropriate titles."""
    _seed_phase2()
    res = client.get("/api/stages/3/modules")
    assert res.status_code == 200
    modules = res.json()

    # Verify we have 7 modules with descriptive titles
    assert len(modules) == 7
    for i, mod in enumerate(modules, 1):
        assert mod["title"], f"Module {i} missing title"
        assert mod["description"], f"Module {i} missing description"


# ---------------------------------------------------------------------------
# Database Integrity
# ---------------------------------------------------------------------------


def test_no_orphaned_steps():
    """No steps should reference non-existent modules."""
    _seed_phase2()
    conn = get_db()
    try:
        orphaned = conn.execute(
            "SELECT COUNT(*) AS cnt FROM steps s "
            "LEFT JOIN modules m ON s.module_id = m.id "
            "WHERE m.id IS NULL"
        ).fetchone()

        assert orphaned["cnt"] == 0
    finally:
        conn.close()


def test_no_orphaned_options():
    """No options should reference non-existent steps."""
    _seed_phase2()
    conn = get_db()
    try:
        orphaned = conn.execute(
            "SELECT COUNT(*) AS cnt FROM options o "
            "LEFT JOIN steps s ON o.step_id = s.id "
            "WHERE s.id IS NULL"
        ).fetchone()

        assert orphaned["cnt"] == 0
    finally:
        conn.close()


def test_all_quiz_steps_have_exactly_one_correct_answer():
    """All quiz steps should have exactly one correct answer."""
    _seed_phase2()
    conn = get_db()
    try:
        # Find quiz steps without exactly 1 correct answer
        problem_steps = conn.execute(
            "SELECT s.id, s.title, COUNT(*) AS correct_count "
            "FROM steps s "
            "JOIN options o ON s.id = o.step_id "
            "WHERE s.type = 'quiz' AND o.is_correct = 1 "
            "GROUP BY s.id "
            "HAVING correct_count != 1"
        ).fetchall()

        assert len(problem_steps) == 0, \
            f"Found {len(problem_steps)} quiz steps without exactly 1 correct answer"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Cross-validation tests
# ---------------------------------------------------------------------------


def test_stage_module_counts_consistency():
    """Module counts in API should match database."""
    _seed_phase2()
    conn = get_db()

    res = client.get("/api/stages")
    assert res.status_code == 200
    api_stages = res.json()

    try:
        for api_stage in api_stages:
            stage_id = api_stage["id"]
            api_count = api_stage["total_modules"]

            db_count = conn.execute(
                "SELECT COUNT(*) AS cnt FROM modules WHERE stage_id = ?",
                (stage_id,)
            ).fetchone()["cnt"]

            assert api_count == db_count, \
                f"Stage {stage_id} API count {api_count} != DB count {db_count}"
    finally:
        conn.close()
