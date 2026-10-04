"""Hello world: send one message to a chat model and inspect the answer.

Run: uv run python 1-fundamentals/1-hello-world.py
Offline (no API key): LLM_PROVIDER=fake uv run python 1-fundamentals/1-hello-world.py
"""

from dotenv import load_dotenv

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def main() -> None:
    # get_chat_model() returns a LangChain chat model for the provider chosen
    # in LLM_PROVIDER. fake_responses is only used when LLM_PROVIDER=fake.
    model = get_chat_model(fake_responses=["Hello! I'm fine, thanks. How can I help you today?"])

    # invoke() sends the input and waits for the full answer. A plain string
    # is turned into a single HumanMessage ("user" role) for us.
    response = model.invoke("Hello, how are you?")

    # The answer is an AIMessage. .content is the raw content (a string, or a
    # list of content blocks for some providers); .text always returns only
    # the text. Providers that report token counts fill .usage_metadata
    # (None for the fake model).
    print("Type:", type(response).__name__)
    print("Content:", response.content)
    print("Text:", response.text)
    print("Token usage:", response.usage_metadata)


if __name__ == "__main__":
    main()
