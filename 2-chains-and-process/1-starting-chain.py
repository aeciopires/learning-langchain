"""First LCEL chain: prompt | model, joined with the "|" (pipe) operator.

Run: uv run python 2-chains-and-process/1-starting-chain.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

question_template = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)


def build_chain(model: BaseChatModel) -> Runnable:
    """prompt | model: like a Linux pipe (cat file | grep x), the output of
    the left side becomes the input of the right side. The prompt receives a
    dict, produces a prompt value, and the model turns it into an AIMessage."""
    return question_template | model


def main() -> None:
    model = get_chat_model(fake_responses=["SockSpectrum"])
    result = build_chain(model).invoke({"product": "colorful socks"})
    print(result)


if __name__ == "__main__":
    main()
