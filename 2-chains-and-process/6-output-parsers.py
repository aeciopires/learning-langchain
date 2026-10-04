"""Output parsers: turn the model's AIMessage into the Python type you need.

Run: uv run python 2-chains-and-process/6-output-parsers.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

explain_prompt = PromptTemplate.from_template("Explain {tool} to a beginner in one sentence.")

# CommaSeparatedListOutputParser also writes the formatting instructions the
# model must follow; get_format_instructions() returns them as text, which we
# inject into the prompt as a "partial" (a placeholder filled in advance).
list_parser = CommaSeparatedListOutputParser()
list_prompt = PromptTemplate(
    template="List 5 {category}.\n{format_instructions}",
    input_variables=["category"],
    partial_variables={"format_instructions": list_parser.get_format_instructions()},
)


def build_text_chain(model: BaseChatModel) -> Runnable:
    """StrOutputParser: AIMessage -> str (the same text as message.text)."""
    return explain_prompt | model | StrOutputParser()


def build_list_chain(model: BaseChatModel) -> Runnable:
    """CommaSeparatedListOutputParser: "a, b, c" -> ["a", "b", "c"]."""
    return list_prompt | model | list_parser


def main() -> None:
    model = get_chat_model(
        fake_responses=[
            "Docker packages an application and its dependencies into a portable container.",
            "Prometheus, Grafana, Loki, Jaeger, OpenTelemetry",
        ]
    )
    print("Prompt sent to the list chain:\n" + list_prompt.format(category="observability tools") + "\n")

    text = build_text_chain(model).invoke({"tool": "Docker"})
    print(f"StrOutputParser -> is a str? {isinstance(text, str)}: {text}")

    items = build_list_chain(model).invoke({"category": "observability tools"})
    print(f"CommaSeparatedListOutputParser -> {type(items).__name__}: {items}")


if __name__ == "__main__":
    main()
