"""ChatPromptTemplate: a template made of messages with roles (system/user).

Run: uv run python 1-fundamentals/4-chat-prompt-template.py
"""

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

# Each tuple is (role, template). The "system" message sets the model's
# behavior; the "user" message carries the actual request.
chat_prompt = ChatPromptTemplate(
    [
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
        ("user", "{sentence}"),
    ]
)


def main() -> None:
    # format_messages() returns a list of messages (SystemMessage, HumanMessage)
    # with every placeholder filled - ready to be sent to a chat model.
    messages = chat_prompt.format_messages(
        input_language="Portuguese",
        output_language="English",
        sentence="Eu estou aprendendo a programar em LangChain.",
    )
    for message in messages:
        print(f"{type(message).__name__}: {message.content}")

    model = get_chat_model(fake_responses=["I am learning to program in LangChain."])
    answer = model.invoke(messages)
    print("Answer:", answer.text)


if __name__ == "__main__":
    main()
