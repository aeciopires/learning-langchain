"""Tests for learning_langchain/cli.py (the "ENTER = default" pattern)."""

import pytest

from learning_langchain.cli import ask, ask_yes_no


def test_ask_returns_what_the_user_typed(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "  typed  ")
    assert ask("Question?", "default") == "typed"


def test_ask_returns_the_default_on_enter(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    assert ask("Question?", "default") == "default"


def test_ask_returns_the_default_without_stdin(no_stdin):
    assert ask("Question?", "default") == "default"


@pytest.mark.parametrize(("typed", "expected"), [("y", True), ("sim", True), ("n", False), ("", False)])
def test_ask_yes_no(monkeypatch, typed, expected):
    monkeypatch.setattr("builtins.input", lambda prompt="": typed)
    assert ask_yes_no("Continue?") is expected


def test_ask_yes_no_default_true(no_stdin):
    assert ask_yes_no("Continue?", default=True) is True
