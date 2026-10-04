"""Configuration read from environment variables (usually loaded from .env).

Every knob has a default, so a fresh clone works with only an API key set.
LLM_PROVIDER=fake runs every example offline, with no API key and no cost.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Providers supported by this repository. "fake" uses LangChain's own fake
# chat model (langchain_core.language_models.fake_chat_models) and fake
# embeddings, so examples and tests run without network access.
SUPPORTED_PROVIDERS = ("google_genai", "openai", "fake")

# Default chat model per provider. Model names change often - check the
# provider's model list before relying on them (REQUIREMENTS.md, section 5).
DEFAULT_CHAT_MODELS = {
    "google_genai": "gemini-3.7-flash",
    "openai": "gpt-5-nano",
    "fake": "fake-chat-model",
}

# Default embedding model per provider (used by the 4-rag module).
DEFAULT_EMBEDDING_MODELS = {
    "google_genai": "models/gemini-embedding-001",
    "openai": "text-embedding-3-large",
    "fake": "deterministic-fake-embedding",
}

DEFAULT_TEMPERATURE = 0.5


@dataclass(frozen=True)
class LLMSettings:
    """The provider, model and temperature every example uses."""

    provider: str
    model: str
    embedding_model: str
    temperature: float


def load_settings() -> LLMSettings:
    """Build LLMSettings from LLM_PROVIDER, LLM_MODEL, LLM_EMBEDDING_MODEL and
    LLM_TEMPERATURE, validating each one with a message naming the variable."""
    provider = os.getenv("LLM_PROVIDER", "google_genai").strip() or "google_genai"
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"LLM_PROVIDER must be one of {', '.join(SUPPORTED_PROVIDERS)}; got '{provider}'.")

    model = os.getenv("LLM_MODEL", "").strip() or DEFAULT_CHAT_MODELS[provider]
    embedding_model = os.getenv("LLM_EMBEDDING_MODEL", "").strip() or DEFAULT_EMBEDDING_MODELS[provider]

    raw_temperature = os.getenv("LLM_TEMPERATURE", "").strip()
    if not raw_temperature:
        temperature = DEFAULT_TEMPERATURE
    else:
        try:
            temperature = float(raw_temperature)
        except ValueError as error:
            raise ValueError(f"LLM_TEMPERATURE must be a number; got '{raw_temperature}'.") from error
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(f"LLM_TEMPERATURE must be between 0 and 2; got {temperature}.")

    return LLMSettings(
        provider=provider,
        model=model,
        embedding_model=embedding_model,
        temperature=temperature,
    )


def is_fake_provider() -> bool:
    """True when the examples run offline with the fake model."""
    return load_settings().provider == "fake"
