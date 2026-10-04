"""RunnableLambda: wrap any Python function so it fits inside a chain.

Run: uv run python 2-chains-and-process/3-runnable-lambda.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


# RunnableLambda wraps a plain Python function so it behaves like any other
# LangChain "Runnable". This lets us plug arbitrary Python logic into a chain
# using the "|" pipe operator, just like prompts and models.
def square(data: dict) -> dict:
    x = data["x"]
    return {"square_result": x * x}


square_runnable = RunnableLambda(square)

# Prompt template that consumes the output produced by the RunnableLambda above.
question_template = PromptTemplate(
    input_variables=["square_result"],
    template="Tell me about the number {square_result}",
)


# A second RunnableLambda used to post-process the model's response, keeping
# only the text content instead of the full AIMessage object.
def extract_content(response) -> str:
    return response.text


to_text = RunnableLambda(extract_content)


def build_chain(model: BaseChatModel) -> Runnable:
    """Chain execution order:
    1) square_runnable: {"x": 25} -> {"square_result": 625}
    2) question_template: builds the prompt text using "square_result"
    3) model: generates the answer for the prompt
    4) to_text: extracts only the text content from the model's response
    """
    return square_runnable | question_template | model | to_text


def main() -> None:
    model = get_chat_model(fake_responses=["625 is a perfect square: 25 x 25."])
    print(build_chain(model).invoke({"x": 25}))


if __name__ == "__main__":
    main()
