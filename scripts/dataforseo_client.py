"""Shared DataForSEO HTTP helpers and credential loading."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request

API_BASE = "https://api.dataforseo.com"

_LOGIN_KEYS = (
    "DATAFORSEO_LOGIN",
    "DATAFORSEO_USERNAME",
    "DATAFORSEO_API_LOGIN",
)
_PASSWORD_KEYS = (
    "DATAFORSEO_PASSWORD",
    "DATAFORSEO_API_PASSWORD",
)


def load_credentials() -> tuple[str, str]:
    login = ""
    for key in _LOGIN_KEYS:
        login = os.environ.get(key, "").strip()
        if login:
            break
    password = ""
    for key in _PASSWORD_KEYS:
        password = os.environ.get(key, "").strip()
        if password:
            break
    return login, password


def credentials_configured() -> bool:
    login, password = load_credentials()
    return bool(login and password)


def auth_header() -> str:
    login, password = load_credentials()
    if not login or not password:
        raise RuntimeError(
            "DataForSEO credentials missing. Set Cloud Agent secrets "
            "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD (Runtime Secret)."
        )
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    return f"Basic {token}"


def post(path: str, payload: list | dict, *, timeout: int = 120) -> dict:
    url = f"{API_BASE}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": auth_header(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HTTP {e.code} {path}: {err_body[:2000]}") from e


def get(path: str, *, timeout: int = 60) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": auth_header()},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HTTP {e.code} {path}: {err_body[:2000]}") from e
