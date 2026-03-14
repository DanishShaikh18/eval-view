"""Tests for EvalView's lightweight version update notice."""

from __future__ import annotations

import json

from evalview import version_check


def test_update_notice_when_newer_version_available(monkeypatch, tmp_path):
    monkeypatch.setattr(version_check, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(version_check, "CACHE_FILE", tmp_path / "version_check.json")
    monkeypatch.setattr(version_check, "_fetch_latest_version", lambda: "0.9.0")
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv(version_check.DISABLE_ENV, raising=False)

    notice = version_check.get_update_notice("0.5.1")

    assert notice == "Update available: evalview 0.5.1 -> 0.9.0  |  pip install -U evalview"
    saved = json.loads((tmp_path / "version_check.json").read_text(encoding="utf-8"))
    assert saved["latest_version"] == "0.9.0"
    assert saved["last_notified_version"] == "0.9.0"


def test_no_notice_in_ci(monkeypatch, tmp_path):
    monkeypatch.setattr(version_check, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(version_check, "CACHE_FILE", tmp_path / "version_check.json")
    monkeypatch.setenv("CI", "true")

    assert version_check.get_update_notice("0.5.1") is None
    assert not (tmp_path / "version_check.json").exists()


def test_cached_latest_version_used_without_network(monkeypatch, tmp_path):
    cache_file = tmp_path / "version_check.json"
    cache_file.write_text(
        json.dumps(
            {
                "latest_version": "0.9.0",
                "last_checked_at": "2099-01-01T00:00:00Z",
                "last_notified_version": None,
                "last_notified_at": None,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(version_check, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(version_check, "CACHE_FILE", cache_file)
    monkeypatch.setattr(version_check, "_fetch_latest_version", lambda: (_ for _ in ()).throw(AssertionError("should not fetch")))
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv(version_check.DISABLE_ENV, raising=False)

    notice = version_check.get_update_notice("0.5.1")

    assert notice == "Update available: evalview 0.5.1 -> 0.9.0  |  pip install -U evalview"


def test_no_notice_when_already_current(monkeypatch, tmp_path):
    monkeypatch.setattr(version_check, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(version_check, "CACHE_FILE", tmp_path / "version_check.json")
    monkeypatch.setattr(version_check, "_fetch_latest_version", lambda: "0.5.1")
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv(version_check.DISABLE_ENV, raising=False)

    assert version_check.get_update_notice("0.5.1") is None
