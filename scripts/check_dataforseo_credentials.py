#!/usr/bin/env python3
"""Verify DataForSEO credentials without printing secrets."""

from __future__ import annotations

import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataforseo_client import credentials_configured, get  # noqa: E402


def main() -> None:
    if not credentials_configured():
        print(
            "FAIL: credentials not in environment. "
            "Add Cloud Agent Runtime Secrets named exactly "
            "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD (or dataforseo_user / "
            "dataforseo_pass), then start a new agent run.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        data = get("/v3/appendix/user_data")
    except urllib.error.URLError as e:
        print(
            "FAIL: cannot reach api.dataforseo.com (TLS/network). "
            f"Credentials are present but the API is unreachable from this host: {e.reason}",
            file=sys.stderr,
        )
        sys.exit(4)
    except RuntimeError as e:
        print(f"FAIL: API error — {e}", file=sys.stderr)
        sys.exit(2)

    status = data.get("status_code")
    if status != 20000:
        print(f"FAIL: unexpected status_code {status}", file=sys.stderr)
        sys.exit(3)

    tasks = data.get("tasks") or []
    task = tasks[0] if tasks else {}
    result = (task.get("result") or [{}])[0] if task.get("result") else {}
    money = result.get("money") or {}
    print("OK: DataForSEO credentials valid.")
    print(f"  balance (USD): {money.get('balance')}")
    print(f"  limits: {result.get('limits')}")


if __name__ == "__main__":
    main()
