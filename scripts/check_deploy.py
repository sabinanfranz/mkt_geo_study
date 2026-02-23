"""Simple deploy smoke checks for Railway environments.

Usage:
  python scripts/check_deploy.py https://your-app.up.railway.app
  BASE_URL=https://your-app.up.railway.app python scripts/check_deploy.py
"""

from __future__ import annotations

import os
import sys

import httpx


def main() -> int:
    base_url = os.getenv("BASE_URL")
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    if not base_url:
        print("BASE_URL is required (arg or env).")
        return 2

    base_url = base_url.rstrip("/")
    endpoints = [
        ("health", "/api/health"),
        ("stages", "/api/stages"),
        ("progress", "/api/progress"),
    ]

    with httpx.Client(timeout=15.0) as client:
        for label, path in endpoints:
            url = f"{base_url}{path}"
            res = client.get(url)
            if res.status_code != 200:
                print(f"[FAIL] {label}: {url} -> {res.status_code}")
                return 1
            print(f"[OK]   {label}: {url}")

    print("Smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
