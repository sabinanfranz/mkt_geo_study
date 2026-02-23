"""Deployment-related DB behavior tests.

These tests verify migration/seed behavior needed for Railway operation.
"""

from __future__ import annotations

from apps.api.database import get_db, init_db
from apps.api.seed import seed


CONTENT_TABLES = ("options", "steps", "modules", "stages")
RESET_TABLES = (
    "user_bookmarks",
    "user_progress",
    "options",
    "steps",
    "modules",
    "stages",
)


def _clear_all() -> None:
    init_db()
    conn = get_db()
    try:
        for table in RESET_TABLES:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
    finally:
        conn.close()


def _content_counts() -> dict[str, int]:
    conn = get_db()
    try:
        return {
            table: conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}").fetchone()["cnt"]
            for table in CONTENT_TABLES
        }
    finally:
        conn.close()


def test_seed_is_idempotent_for_content_tables():
    _clear_all()

    seed(run_migrations=False)
    first = _content_counts()

    seed(run_migrations=False)
    second = _content_counts()

    assert first == second


def test_migration_history_is_recorded():
    init_db()
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM schema_migrations"
        ).fetchone()
        assert row is not None
        assert row["cnt"] >= 1
    finally:
        conn.close()


def test_seed_preserves_user_progress_rows():
    _clear_all()
    seed(run_migrations=False)

    conn = get_db()
    try:
        first_step = conn.execute(
            "SELECT id FROM steps ORDER BY id LIMIT 1"
        ).fetchone()
        assert first_step is not None

        conn.execute(
            "INSERT INTO user_progress "
            "(user_id, step_id, selected_option_id, is_correct, time_spent_seconds) "
            "VALUES (?, ?, NULL, NULL, ?)",
            ("default", first_step["id"], 42),
        )
        conn.commit()
    finally:
        conn.close()

    seed(run_migrations=False)

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT step_id, time_spent_seconds FROM user_progress "
            "WHERE user_id = 'default' ORDER BY id LIMIT 1"
        ).fetchone()
        assert row is not None
        assert row["step_id"] == first_step["id"]
        assert row["time_spent_seconds"] == 42
    finally:
        conn.close()


def test_seed_balances_quiz_answer_labels():
    _clear_all()
    seed(run_migrations=False)

    conn = get_db()
    try:
        quiz_steps = conn.execute(
            "SELECT id FROM steps WHERE type = 'quiz' ORDER BY id"
        ).fetchall()
        assert len(quiz_steps) > 0

        counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        rows = conn.execute(
            "SELECT o.label, COUNT(*) AS cnt "
            "FROM options o "
            "JOIN steps s ON s.id = o.step_id "
            "WHERE s.type = 'quiz' AND o.is_correct = 1 "
            "GROUP BY o.label"
        ).fetchall()
        for row in rows:
            counts[row["label"]] = row["cnt"]

        abc_counts = [counts["A"], counts["B"], counts["C"]]
        assert max(abc_counts) - min(abc_counts) <= 1
        assert counts["D"] == 0
        assert sum(abc_counts) == len(quiz_steps)

        for step in quiz_steps:
            options = conn.execute(
                "SELECT label, is_correct FROM options WHERE step_id = ? ORDER BY order_idx",
                (step["id"],),
            ).fetchall()
            assert len(options) == 4
            assert sorted([opt["label"] for opt in options]) == ["A", "B", "C", "D"]
            assert sum(1 for opt in options if opt["is_correct"] == 1) == 1
    finally:
        conn.close()
