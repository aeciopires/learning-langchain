"""The @chain decorator turns a plain Python function into a Runnable.

Run: uv run python 2-chains-and-process/2-chains-with-decorators.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, chain

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


# After @chain, `square` is a Runnable: it can be piped with "|" and gets
# invoke(), batch() and stream() for free.
@chain
def square(data: dict) -> dict:
    x = data["x"]
    return {"square_result": x * x}


question_template = PromptTemplate(
    input_variables=["square_result"],
    template="Tell me about the number {square_result}",
)


def build_chain(model: BaseChatModel) -> Runnable:
    """square -> prompt -> model: plain Python logic runs before the LLM."""
    return square | question_template | model


def main() -> None:
    model = get_chat_model(fake_responses=["625 is 25 squared and also 5 to the fourth power."])
    result = build_chain(model).invoke({"x": 25})
    print(result)


if __name__ == "__main__":
    main()
