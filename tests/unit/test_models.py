"""Tests for learning_langchain/models.py."""

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage

from learning_langchain.models import (
    DEFAULT_FAKE_RESPONSE,
    FakeToolCallingModel,
    build_fake_chat_model,
    get_chat_model,
    get_embeddings,
)


def test_fake_model_answers_in_order_and_repeats():
    model = build_fake_chat_model(["first", "second"])
    answers = [model.invoke("hi").text for _ in range(3)]
    assert answers == ["first", "second", "first"]


def test_fake_model_without_responses_uses_the_default_answer():
    assert build_fake_chat_model().invoke("hi").text == DEFAULT_FAKE_RESPONSE


def test_fake_model_returns_scripted_tool_calls():
    scripted = AIMessage(content="", tool_calls=[{"name": "ping", "args": {"host": "a"}, "id": "1"}])
    answer = build_fake_chat_model([scripted]).invoke("hi")
    assert answer.tool_calls[0]["name"] == "ping"
    assert answer.tool_calls[0]["args"] == {"host": "a"}


def test_bind_tools_returns_the_same_fake_model():
    model = build_fake_chat_model(["x"])
    assert model.bind_tools([]) is model


def test_get_chat_model_is_fake_offline():
    assert isinstance(get_chat_model(fake_responses=["ok"]), FakeToolCallingModel)


@pytest.mark.parametrize(
    ("provider", "class_name", "key_variable"),
    [
        ("google_genai", "ChatGoogleGenerativeAI", "GOOGLE_API_KEY"),
        ("openai", "ChatOpenAI", "OPENAI_API_KEY"),
    ],
)
def test_get_chat_model_builds_the_provider_class(monkeypatch, provider, class_name, key_variable):
    # Building a model doesn't call the API, so a dummy key is enough.
    monkeypatch.setenv(key_variable, "dummy-key-for-tests")
    monkeypatch.setenv("LLM_PROVIDER", provider)
    model = get_chat_model(model_name="some-model")
    assert type(model).__name__ == class_name


@pytest.mark.parametrize(
    ("provider", "class_name", "key_variable"),
    [
        ("google_genai", "GoogleGenerativeAIEmbeddings", "GOOGLE_API_KEY"),
        ("openai", "OpenAIEmbeddings", "OPENAI_API_KEY"),
    ],
)
def test_get_embeddings_builds_the_provider_class(monkeypatch, provider, class_name, key_variable):
    monkeypatch.setenv(key_variable, "dummy-key-for-tests")
    monkeypatch.setenv("LLM_PROVIDER", provider)
    assert type(get_embeddings()).__name__ == class_name


def test_fake_embeddings_are_deterministic():
    embeddings = get_embeddings()
    assert isinstance(embeddings, DeterministicFakeEmbedding)
    assert embeddings.embed_query("same text") == embeddings.embed_query("same text")
    assert embeddings.embed_query("same text") != embeddings.embed_query("other text")
