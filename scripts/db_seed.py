"""Run content seed as idempotent upsert."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.seed import seed


if __name__ == "__main__":
    seed(run_migrations=True)
