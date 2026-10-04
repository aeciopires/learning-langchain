"""Tests for the 2-chains-and-process module."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from learning_langchain.models import build_fake_chat_model
from tests._helpers import echo_model, load_script


def test_starting_chain_sends_the_formatted_prompt():
    script = load_script("2-chains-and-process/1-starting-chain.py")
    result = script.build_chain(echo_model()).invoke({"product": "socks"})
    assert result.content == "What is a good name for a company that makes socks?"


def test_decorated_function_runs_before_the_prompt():
    script = load_script("2-chains-and-process/2-chains-with-decorators.py")
    assert script.square.invoke({"x": 4}) == {"square_result": 16}
    result = script.build_chain(echo_model()).invoke({"x": 25})
    assert result.content == "Tell me about the number 625"


def test_runnable_lambda_chain_returns_plain_text():
    script = load_script("2-chains-and-process/3-runnable-lambda.py")
    model = GenericFakeChatModel(messages=iter(["six hundred twenty-five"]))
    assert script.build_chain(model).invoke({"x": 25}) == "six hundred twenty-five"


def test_translation_chain_cleans_input_and_uses_both_languages():
    script = load_script("2-chains-and-process/4-chain-of-translate.py")
    result = script.build_chain(echo_model()).invoke(
        {"input_language": " English ", "output_language": "Portuguese ", "sentence": "  Hi  "}
    )
    assert "from English to Portuguese" in result
    assert "Sentence: Hi\n" in result


def test_map_reduce_calls_the_model_once_per_document_plus_reduce():
    script = load_script("2-chains-and-process/5-sumarization-map-reduce-pipeline.py")
    model = GenericFakeChatModel(messages=iter(["sum 1", "sum 2", "sum 3", "final"]))
    result = script.build_pipeline(model).invoke(["doc 1", "doc 2", "doc 3"])
    assert result.text == "final"


def test_reduce_prompt_receives_every_partial_summary():
    script = load_script("2-chains-and-process/5-sumarization-map-reduce-pipeline.py")
    assert script.format_summaries(["a", "b"]) == {"summaries": "- a\n\n- b"}


def test_map_reduce_main_runs_with_defaults(no_stdin, capsys):
    load_script("2-chains-and-process/5-sumarization-map-reduce-pipeline.py").main()
    assert "=== FINAL SUMMARY ===" in capsys.readouterr().out


def test_output_parsers():
    script = load_script("2-chains-and-process/6-output-parsers.py")
    text_model = GenericFakeChatModel(messages=iter(["Docker runs containers."]))
    assert script.build_text_chain(text_model).invoke({"tool": "Docker"}) == "Docker runs containers."
    list_model = GenericFakeChatModel(messages=iter(["a, b, c"]))
    assert script.build_list_chain(list_model).invoke({"category": "x"}) == ["a", "b", "c"]


def test_structured_output_returns_a_validated_object():
    script = load_script("2-chains-and-process/7-structured-output.py")
    incident = script.build_chain(build_fake_chat_model([script.FAKE_STRUCTURED_ANSWER])).invoke(
        {"alert": "x"}
    )
    assert isinstance(incident, script.Incident)
    assert incident.service == "checkout-api"
    assert incident.needs_rollback is True


def test_structured_output_rejects_invalid_data():
    script = load_script("2-chains-and-process/7-structured-output.py")
    bad = AIMessage(
        content="",
        tool_calls=[{"name": "Incident", "args": {"service": "x", "severity": "apocalyptic"}, "id": "1"}],
    )
    try:
        script.build_chain(build_fake_chat_model([bad])).invoke({"alert": "x"})
    except Exception as error:  # pydantic.ValidationError, wrapped or not
        assert "severity" in str(error)
    else:
        raise AssertionError("an invalid severity should be rejected")


def test_parallel_chain_returns_one_key_per_branch():
    script = load_script("2-chains-and-process/8-runnable-parallel.py")
    result = script.build_chain(echo_model()).invoke({"technology": "Kubernetes"})
    assert set(result) == {"technology", "pros", "cons"}
    assert "advantages of Kubernetes" in result["pros"]
    assert "disadvantages of Kubernetes" in result["cons"]
