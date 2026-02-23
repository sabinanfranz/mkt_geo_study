"""Run database migrations."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.database import init_db, get_database_backend


if __name__ == "__main__":
    init_db()
    print(f"Migrations applied ({get_database_backend()}).")
