#!/usr/bin/env python3
"""
Spike: DataForSEO SERP + On-Page Instant Pages for one target keyword.

Requires env: DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

API_BASE = "https://api.dataforseo.com"


def _auth_header() -> str:
    login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
    password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
    if not login or not password:
        print(
            "Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD to run this spike.",
            file=sys.stderr,
        )
        sys.exit(1)
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    return f"Basic {token}"


def _post(path: str, payload: list | dict) -> dict:
    url = f"{API_BASE}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": _auth_header(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code} {path}: {err_body[:2000]}", file=sys.stderr)
        raise


def _normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")


def _field_presence(item: dict) -> dict[str, bool]:
    """Best-effort keys; adjust after first live response against real API shape."""
    result = item.get("result") or item
    if isinstance(result, list) and result:
        result = result[0]
    items = result.get("items") if isinstance(result, dict) else None
    page = items[0] if isinstance(items, list) and items else result
    if not isinstance(page, dict):
        return {"parseable_page_object": False}

    def has(*keys: str) -> bool:
        for k in keys:
            if page.get(k):
                return True
        return False

    meta = page.get("meta") if isinstance(page.get("meta"), dict) else {}
    content = page.get("content") if isinstance(page.get("content"), dict) else {}

    return {
        "status_code": page.get("status_code") == 200,
        "title": has("title") or bool(meta.get("title")),
        "description": bool(meta.get("description")),
        "h1": has("h1") or bool(page.get("htags", {}).get("h1")),
        "headings": bool(page.get("htags")),
        "plain_text": has("plain_text", "plain_text_word_count")
        or bool(content.get("plain_text")),
        "structured_data": has("structured_data", "schema") or bool(page.get("schema")),
        "size_bytes": bool(page.get("size")),
    }


def run_serp(
    keyword: str,
    region: str,
    language: str,
    device: str,
) -> tuple[list[str], dict]:
    """Returns organic URLs (up to 10) and raw API envelope."""
    # Location/language mapping is account-specific; spike uses common DFS shape.
    location_name = {
        "US": "United States",
        "GB": "United Kingdom",
        "AE": "United Arab Emirates",
    }.get(region.upper(), "United States")

    payload = [
        {
            "keyword": keyword,
            "location_name": location_name,
            "language_code": language,
            "device": device,
            "os": "android" if device == "mobile" else "windows",
            "depth": 10,
        }
    ]
    raw = _post("/v3/serp/google/organic/live/advanced", payload)
    urls: list[str] = []
    tasks = raw.get("tasks") or []
    for task in tasks:
        for result in task.get("result") or []:
            for item in result.get("items") or []:
                if item.get("type") == "organic" and item.get("url"):
                    urls.append(item["url"])
    return urls[:10], raw


def run_instant_pages(url: str, enable_js: bool) -> dict:
    payload = [
        {
            "url": url,
            "enable_javascript": enable_js,
            "enable_browser_rendering": enable_js,
        }
    ]
    return _post("/v3/on_page/instant_pages", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--region", default="US")
    parser.add_argument("--language", default="en")
    parser.add_argument("--device", default="mobile", choices=("mobile", "desktop"))
    parser.add_argument("--enable-js", action="store_true", default=True)
    parser.add_argument("--no-enable-js", action="store_false", dest="enable_js")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/spike"),
    )
    args = parser.parse_args()

    target_norm = _normalize_url(args.target_url)
    serp_urls, serp_raw = run_serp(
        args.keyword, args.region, args.language, args.device
    )
    peers = [
        u
        for u in serp_urls
        if _normalize_url(u) != target_norm
    ]

    fetches: list[dict] = []
    all_urls = [("target", args.target_url)] + [
        ("peer", u) for u in peers
    ]
    for role, url in all_urls:
        try:
            raw = run_instant_pages(url, args.enable_js)
            tasks = raw.get("tasks") or []
            task0 = tasks[0] if tasks else {}
            presence = _field_presence(task0)
            fetches.append(
                {
                    "role": role,
                    "url": url,
                    "cost": task0.get("cost"),
                    "status_code_task": task0.get("status_code"),
                    "field_presence": presence,
                    "raw_task": task0,
                }
            )
        except Exception as e:  # noqa: BLE001 — spike script
            fetches.append(
                {
                    "role": role,
                    "url": url,
                    "error": str(e),
                }
            )

    report = {
        "spike": "dataforseo_serp_and_instant_pages",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": {
            "keyword": args.keyword,
            "target_url": args.target_url,
            "region": args.region,
            "language": args.language,
            "device": args.device,
            "enable_javascript": args.enable_js,
        },
        "serp": {
            "organic_count": len(serp_urls),
            "peer_count_after_target_exclusion": len(peers),
            "urls": serp_urls,
            "cost": (serp_raw.get("tasks") or [{}])[0].get("cost"),
        },
        "fetches": fetches,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"dataforseo_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    ok = sum(
        1
        for f in fetches
        if f.get("field_presence", {}).get("status_code")
        or f.get("field_presence", {}).get("plain_text")
    )
    print(f"Fetch summary: {ok}/{len(fetches)} with 200 or plain_text (see JSON for details)")


if __name__ == "__main__":
    main()
