"""Tests for the 1-fundamentals module."""

from tests._helpers import load_script


def test_hello_world_prints_the_fake_answer(capsys):
    load_script("1-fundamentals/1-hello-world.py").main()
    output = capsys.readouterr().out
    assert "Type: AIMessage" in output
    assert "How can I help you today?" in output


def test_init_chat_model_offline_uses_the_fake_model(capsys):
    load_script("1-fundamentals/2-init-chat-model.py").main()
    assert "[fake model] FakeToolCallingModel: Hi from the fake model!" in capsys.readouterr().out


def test_init_chat_model_builds_both_styles(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy-key-for-tests")
    monkeypatch.setenv("LLM_PROVIDER", "google_genai")
    script = load_script("1-fundamentals/2-init-chat-model.py")
    settings = script.load_settings()
    assert type(script.build_with_init_chat_model(settings)).__name__ == "ChatGoogleGenerativeAI"
    assert type(script.build_with_provider_class(settings)).__name__ == "ChatGoogleGenerativeAI"


def test_prompt_template_fills_the_placeholder():
    script = load_script("1-fundamentals/3-prompt-template.py")
    assert script.template.format(product="socks") == "What is a good name for a company that makes socks?"


def test_chat_prompt_template_builds_system_and_user_messages():
    script = load_script("1-fundamentals/4-chat-prompt-template.py")
    messages = script.chat_prompt.format_messages(
        input_language="Portuguese", output_language="English", sentence="Oi"
    )
    assert [type(m).__name__ for m in messages] == ["SystemMessage", "HumanMessage"]
    assert "translates Portuguese to English" in messages[0].content
    assert messages[1].content == "Oi"


def test_messages_history_grows_with_every_turn():
    script = load_script("1-fundamentals/5-messages.py")
    model = script.get_chat_model(fake_responses=["a1", "a2"])
    history = []
    script.chat(model, history, "q1")
    script.chat(model, history, "q2")
    # q1, a1, q2, a2: the model received the whole history on the 2nd call.
    assert [m.text for m in history] == ["q1", "a1", "q2", "a2"]


def test_streaming_and_batch(capsys):
    load_script("1-fundamentals/6-streaming-and-batch.py").main()
    output = capsys.readouterr().out
    assert "Containers package an application" in output
    assert "Terraform describes infrastructure as code." in output
