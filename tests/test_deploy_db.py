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
