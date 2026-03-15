from __future__ import annotations

import logging


def test_extract_json_from_text_uses_fallback_without_warning(caplog):
    from evalview.core.llm_provider import LLMClient, LLMProvider

    client = LLMClient(provider=LLMProvider.OLLAMA, api_key="ollama", model="llama3.2")

    malformed = """{
  "score": 80,
  "rationale": This is not valid JSON because the string is not quoted properly
}"""

    with caplog.at_level(logging.WARNING):
        payload = client._extract_json_from_text(malformed)

    assert payload["score"] == 70
    assert "Auto-extracted from non-JSON response" in payload["reasoning"]
    assert "Could not parse JSON from Ollama response" not in caplog.text
