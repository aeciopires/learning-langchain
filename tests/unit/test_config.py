"""Tests for learning_langchain/config.py: defaults and validation."""

import pytest

from learning_langchain.config import (
    DEFAULT_CHAT_MODELS,
    DEFAULT_EMBEDDING_MODELS,
    DEFAULT_TEMPERATURE,
    is_fake_provider,
    load_settings,
)


def test_defaults_when_provider_is_not_set(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER")
    settings = load_settings()
    assert settings.provider == "google_genai"
    assert settings.model == DEFAULT_CHAT_MODELS["google_genai"]
    assert settings.embedding_model == DEFAULT_EMBEDDING_MODELS["google_genai"]
    assert settings.temperature == DEFAULT_TEMPERATURE


@pytest.mark.parametrize("provider", ["google_genai", "openai", "fake"])
def test_each_provider_has_its_default_model(monkeypatch, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    assert load_settings().model == DEFAULT_CHAT_MODELS[provider]


def test_overrides_from_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "my-model")
    monkeypatch.setenv("LLM_EMBEDDING_MODEL", "my-embeddings")
    monkeypatch.setenv("LLM_TEMPERATURE", "0")
    settings = load_settings()
    assert (settings.model, settings.embedding_model, settings.temperature) == (
        "my-model",
        "my-embeddings",
        0.0,
    )


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "skynet")
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        load_settings()


@pytest.mark.parametrize("value", ["hot", "-0.1", "2.5"])
def test_invalid_temperature_is_rejected(monkeypatch, value):
    monkeypatch.setenv("LLM_TEMPERATURE", value)
    with pytest.raises(ValueError, match="LLM_TEMPERATURE"):
        load_settings()


def test_is_fake_provider():
    assert is_fake_provider() is True
