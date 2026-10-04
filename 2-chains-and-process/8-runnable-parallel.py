"""RunnableParallel: run several chains on the same input at the same time.

Run: uv run python 2-chains-and-process/8-runnable-parallel.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

pros_prompt = PromptTemplate.from_template("List 2 advantages of {technology}, one line each.")
cons_prompt = PromptTemplate.from_template("List 2 disadvantages of {technology}, one line each.")


def build_chain(model: BaseChatModel) -> Runnable:
    """RunnableParallel runs each branch with the same input and returns a dict
    with one key per branch - like a team splitting a task: each person works
    on their part at the same time, and the results are collected at the end.
    RunnablePassthrough() just copies the input, so we keep it in the output."""
    return RunnableParallel(
        technology=RunnablePassthrough(),
        pros=pros_prompt | model | StrOutputParser(),
        cons=cons_prompt | model | StrOutputParser(),
    )


def main() -> None:
    # Offline mode: both branches get the same fake text, since the branches
    # run concurrently and the order they reach the model is not fixed.
    model = get_chat_model(fake_responses=["- (fake) first point\n- (fake) second point"])
    result = build_chain(model).invoke({"technology": "serverless functions"})

    print("Input:", result["technology"])
    print("Pros:\n" + result["pros"])
    print("Cons:\n" + result["cons"])


if __name__ == "__main__":
    main()
