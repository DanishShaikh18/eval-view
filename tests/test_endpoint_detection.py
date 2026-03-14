"""Tests for local agent endpoint discovery."""

from __future__ import annotations

import httpx

from evalview.commands.shared import _detect_agent_endpoint


class _SocketStub:
    def __init__(self, open_ports):
        self._open_ports = open_ports
        self._port = None

    def settimeout(self, timeout):
        return None

    def connect_ex(self, address):
        self._port = address[1]
        return 0 if self._port in self._open_ports else 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_detect_agent_endpoint_finds_execute(monkeypatch):
    monkeypatch.setattr("socket.socket", lambda *args, **kwargs: _SocketStub({8000}))

    def fake_post(url, json, timeout):
        if url == "http://localhost:8000/execute":
            return httpx.Response(200, json={"response": "pong"})
        raise httpx.ConnectError("no route")

    monkeypatch.setattr("evalview.commands.shared.httpx.post", fake_post)
    monkeypatch.setattr("evalview.commands.shared.httpx.get", lambda *args, **kwargs: httpx.Response(404))

    assert _detect_agent_endpoint() == "http://localhost:8000/execute"


def test_detect_agent_endpoint_falls_back_to_health(monkeypatch):
    monkeypatch.setattr("socket.socket", lambda *args, **kwargs: _SocketStub({8000}))
    monkeypatch.setattr("evalview.commands.shared.httpx.post", lambda *args, **kwargs: httpx.Response(404))

    def fake_get(url, timeout):
        if url == "http://localhost:8000/health":
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(404)

    monkeypatch.setattr("evalview.commands.shared.httpx.get", fake_get)

    assert _detect_agent_endpoint() == "http://localhost:8000"
