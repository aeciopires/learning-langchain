"""stream() and batch(): the other two ways to call any chat model.

Run: uv run python 1-fundamentals/6-streaming-and-batch.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import LanguageModelInput

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def main() -> None:
    model = get_chat_model(
        fake_responses=[
            "Containers package an application with everything it needs to run.",
            "Terraform describes infrastructure as code.",
            "Ansible automates server configuration.",
        ]
    )

    # stream(): yields the answer in chunks (AIMessageChunk) as soon as the
    # provider produces them - like watching a video while it downloads,
    # instead of waiting for the whole file.
    print("stream():")
    for chunk in model.stream("In one sentence, what is a container?"):
        print(chunk.text, end="", flush=True)
    print()

    # batch(): sends several independent inputs (in parallel by default) and
    # returns the answers in the same order as the inputs. max_concurrency
    # limits how many calls run at once - useful to respect provider rate
    # limits (and here it keeps the offline fake answers in order).
    print("\nbatch():")
    questions: list[LanguageModelInput] = [
        "In one sentence, what is Terraform?",
        "In one sentence, what is Ansible?",
    ]
    answers = model.batch(questions, config={"max_concurrency": 1})
    for question, answer in zip(questions, answers, strict=True):
        print(f"- {question}\n  {answer.text}")


if __name__ == "__main__":
    main()
