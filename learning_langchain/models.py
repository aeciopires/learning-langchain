"""One place to create chat models and embeddings for every example.

Think of get_chat_model() as a universal power adapter: the scripts plug
into it the same way, and LLM_PROVIDER decides which "socket" (Google
Gemini, OpenAI or an offline fake) is on the other side.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.embeddings import DeterministicFakeEmbedding, Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from learning_langchain.config import LLMSettings, load_settings

# What the fake model answers when a script gives no scripted responses.
DEFAULT_FAKE_RESPONSE = "This is a fake answer: set LLM_PROVIDER to a real provider to call an LLM."


class FakeToolCallingModel(GenericFakeChatModel):
    """GenericFakeChatModel that also accepts bind_tools().

    create_agent() calls model.bind_tools(tools) before every model call.
    GenericFakeChatModel does not implement it (the base class raises
    NotImplementedError), so this subclass returns itself: the scripted
    responses - including AIMessages with tool_calls - are what drive the
    agent loop in offline mode and in the unit tests.
    """

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> FakeToolCallingModel:  # type: ignore[override]
        return self


def build_fake_chat_model(responses: Sequence[str | AIMessage] | None = None) -> FakeToolCallingModel:
    """A fake chat model that answers with `responses`, in order, forever.

    itertools.cycle() repeats the list, so a script that calls the model more
    times than there are responses never runs out of answers.
    """
    scripted = list(responses) if responses else [DEFAULT_FAKE_RESPONSE]
    return FakeToolCallingModel(messages=itertools.cycle(scripted))


def get_chat_model(
    fake_responses: Sequence[str | AIMessage] | None = None,
    settings: LLMSettings | None = None,
    model_name: str | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Return the chat model chosen by LLM_PROVIDER/LLM_MODEL/LLM_TEMPERATURE.

    - google_genai / openai: init_chat_model("provider:model", ...), the
      provider-agnostic factory from LangChain (langchain.chat_models).
    - fake: build_fake_chat_model(fake_responses), no network and no key.

    model_name overrides LLM_MODEL; extra keyword arguments (e.g.
    temperature=0.0) are passed to init_chat_model() and override the settings.
    """
    settings = settings or load_settings()
    if settings.provider == "fake":
        return build_fake_chat_model(fake_responses)
    params: dict[str, Any] = {"temperature": settings.temperature}
    params.update(kwargs)
    return init_chat_model(f"{settings.provider}:{model_name or settings.model}", **params)


def get_embeddings(settings: LLMSettings | None = None) -> Embeddings:
    """Return the embeddings model for LLM_PROVIDER (used by the 4-rag module)."""
    settings = settings or load_settings()
    if settings.provider == "google_genai":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
    if settings.provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=settings.embedding_model)
    # DeterministicFakeEmbedding: the same text always gets the same vector,
    # but similar texts do NOT get similar vectors - good for tests, useless
    # for real semantic search.
    return DeterministicFakeEmbedding(size=256)
