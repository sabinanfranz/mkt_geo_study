"""Database connection helpers and backend-aware migrations."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable, Sequence

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional in local SQLite mode
    psycopg = None
    dict_row = None

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "geo_mentor.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
TRUTHY_VALUES = {"1", "true", "yes", "on"}


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url[len("postgres://") :]
    return database_url


def _is_postgres_url(database_url: str) -> bool:
    return database_url.startswith(("postgresql://", "postgres://"))


def _resolve_sqlite_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        return Path(database_url[len("sqlite:///") :]).expanduser().resolve()
    sqlite_path = os.getenv("SQLITE_PATH", "").strip()
    if sqlite_path:
        return Path(sqlite_path).expanduser().resolve()
    return DEFAULT_DB_PATH


def get_database_backend() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if _is_postgres_url(database_url):
        return "postgres"
    return "sqlite"


def is_truthy_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_VALUES


def _convert_qmark_to_postgres(query: str) -> str:
    """Convert DB-API qmark placeholders to psycopg placeholders.

    This keeps existing SQLite-style SQL in application code portable.
    """
    if "?" not in query:
        return query

    out: list[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(query):
        ch = query[i]
        if ch == "'" and not in_double:
            out.append(ch)
            if in_single and i + 1 < len(query) and query[i + 1] == "'":
                out.append("'")
                i += 2
                continue
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
            i += 1
            continue
        if ch == "?" and not in_single and not in_double:
            out.append("%s")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _split_sql_statements(sql_script: str) -> list[str]:
    """Split SQL script by semicolon, ignoring semicolons inside quotes."""
    statements: list[str] = []
    chunk: list[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(sql_script):
        ch = sql_script[i]
        if ch == "'" and not in_double:
            chunk.append(ch)
            if in_single and i + 1 < len(sql_script) and sql_script[i + 1] == "'":
                chunk.append("'")
                i += 2
                continue
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            chunk.append(ch)
            i += 1
            continue
        if ch == ";" and not in_single and not in_double:
            stmt = "".join(chunk).strip()
            if stmt:
                statements.append(stmt)
            chunk = []
            i += 1
            continue
        chunk.append(ch)
        i += 1

    tail = "".join(chunk).strip()
    if tail:
        statements.append(tail)
    return statements


class PostgresConnection:
    """Tiny compatibility layer with sqlite3.Connection API used by the app."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, query: str, params: Sequence | Iterable | None = None):
        converted = _convert_qmark_to_postgres(query)
        if params is None:
            return self._conn.execute(converted)
        return self._conn.execute(converted, tuple(params))

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


def get_db() -> sqlite3.Connection | PostgresConnection:
    """Return a backend-aware DB connection.

    Priority:
    1) DATABASE_URL postgres* -> PostgreSQL
    2) DATABASE_URL sqlite:///... or SQLITE_PATH -> SQLite path
    3) default SQLite path data/geo_mentor.db
    """
    database_url = os.getenv("DATABASE_URL", "").strip()

    if _is_postgres_url(database_url):
        if psycopg is None:
            raise RuntimeError(
                "DATABASE_URL is set to PostgreSQL but psycopg is not installed. "
                "Install dependencies from requirements.txt."
            )
        normalized = _normalize_database_url(database_url)
        conn = psycopg.connect(normalized, row_factory=dict_row)
        return PostgresConnection(conn)

    db_path = _resolve_sqlite_path(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema_migrations_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def _execute_sql_script(conn, backend: str, sql_script: str) -> None:
    if backend == "sqlite":
        conn.executescript(sql_script)
        return

    for stmt in _split_sql_statements(sql_script):
        conn.execute(stmt)


def run_migrations() -> None:
    """Apply backend-specific SQL migrations exactly once per version."""
    backend = get_database_backend()
    conn = get_db()
    try:
        _ensure_schema_migrations_table(conn)
        applied_rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
        applied_versions = {row["version"] for row in applied_rows}

        if MIGRATIONS_DIR.exists():
            migration_files = sorted(MIGRATIONS_DIR.glob(f"*.{backend}.sql"))
        else:
            migration_files = []

        for migration_file in migration_files:
            suffix = f".{backend}.sql"
            version = migration_file.name[: -len(suffix)]
            if version in applied_versions:
                continue
            sql_script = migration_file.read_text(encoding="utf-8")
            _execute_sql_script(conn, backend, sql_script)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (version,),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize schema via migrations (idempotent)."""
    run_migrations()
