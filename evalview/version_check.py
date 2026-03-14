"""Lightweight PyPI version update checks for human-facing CLI commands."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

PYPI_URL = "https://pypi.org/pypi/evalview/json"
CACHE_DIR = Path.home() / ".evalview"
CACHE_FILE = CACHE_DIR / "version_check.json"
CHECK_INTERVAL = timedelta(hours=24)
RENOTICE_INTERVAL = timedelta(days=7)
DISABLE_ENV = "EVALVIEW_DISABLE_UPDATE_CHECK"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _version_key(version: str) -> tuple[int, ...]:
    parts = []
    for chunk in version.replace("-", ".").split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        if digits:
            parts.append(int(digits))
        else:
            parts.append(0)
    return tuple(parts)


def _is_newer(latest: str, current: str) -> bool:
    if current == "dev":
        return False
    latest_key = _version_key(latest)
    current_key = _version_key(current)
    max_len = max(len(latest_key), len(current_key))
    latest_key = latest_key + (0,) * (max_len - len(latest_key))
    current_key = current_key + (0,) * (max_len - len(current_key))
    return latest_key > current_key


def _is_ci() -> bool:
    return os.environ.get("CI", "").lower() in ("1", "true", "yes")


@dataclass
class VersionCheckCache:
    latest_version: Optional[str] = None
    last_checked_at: Optional[str] = None
    last_notified_version: Optional[str] = None
    last_notified_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "VersionCheckCache":
        return cls(
            latest_version=data.get("latest_version"),
            last_checked_at=data.get("last_checked_at"),
            last_notified_version=data.get("last_notified_version"),
            last_notified_at=data.get("last_notified_at"),
        )


def _load_cache() -> VersionCheckCache:
    if not CACHE_FILE.exists():
        return VersionCheckCache()
    try:
        return VersionCheckCache.from_dict(json.loads(CACHE_FILE.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return VersionCheckCache()


def _save_cache(cache: VersionCheckCache) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(asdict(cache), indent=2), encoding="utf-8")
    except OSError:
        pass


def _fetch_latest_version() -> Optional[str]:
    try:
        with urlopen(PYPI_URL, timeout=1.5) as response:  # nosec B310 - fixed PyPI URL only
            data = json.loads(response.read().decode("utf-8"))
            return data.get("info", {}).get("version")
    except Exception:
        return None


def _should_refresh(cache: VersionCheckCache) -> bool:
    last_checked = _parse_iso(cache.last_checked_at)
    if last_checked is None:
        return True
    return (_utc_now() - last_checked) >= CHECK_INTERVAL


def _should_show_notice(cache: VersionCheckCache, latest_version: str, current_version: str) -> bool:
    if not _is_newer(latest_version, current_version):
        return False
    last_notified_at = _parse_iso(cache.last_notified_at)
    if cache.last_notified_version != latest_version:
        return True
    if last_notified_at is None:
        return True
    return (_utc_now() - last_notified_at) >= RENOTICE_INTERVAL


def should_check_for_updates() -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    if _is_ci():
        return False
    if os.environ.get(DISABLE_ENV, "").lower() in ("1", "true", "yes"):
        return False
    return True


def get_update_notice(current_version: str) -> Optional[str]:
    """Return a single-line upgrade notice if a newer PyPI release exists."""
    if not should_check_for_updates():
        return None

    cache = _load_cache()
    latest_version = cache.latest_version

    if _should_refresh(cache):
        fetched = _fetch_latest_version()
        cache.last_checked_at = _utc_now_iso()
        if fetched:
            cache.latest_version = fetched
            latest_version = fetched
        _save_cache(cache)

    if not latest_version or not _should_show_notice(cache, latest_version, current_version):
        return None

    cache.last_notified_version = latest_version
    cache.last_notified_at = _utc_now_iso()
    _save_cache(cache)
    return f"Update available: evalview {current_version} -> {latest_version}  |  pip install -U evalview"
