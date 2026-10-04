"""Fixtures shared by every test.

Tests never call a real LLM: LLM_PROVIDER is forced to "fake" and the other
LLM_* variables are removed, so a test's result doesn't depend on your .env.
"""

from __future__ import annotations

import pytest

LLM_VARIABLES = ("LLM_PROVIDER", "LLM_MODEL", "LLM_EMBEDDING_MODEL", "LLM_TEMPERATURE")


@pytest.fixture(autouse=True)
def offline_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run every test offline, with the fake model and fake embeddings."""
    for name in LLM_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "fake")


@pytest.fixture
def no_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make input() behave as if stdin were closed, so interactive scripts
    take every default answer (the same as `make run-all`)."""

    def closed_stdin(prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", closed_stdin)
