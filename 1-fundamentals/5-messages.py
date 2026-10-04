"""Messages and conversation history: the model only "remembers" what you send.

Run: uv run python 1-fundamentals/5-messages.py
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def chat(model, history: list[BaseMessage], user_text: str) -> str:
    """Append the user's message, call the model with the WHOLE history, and
    append the model's answer - so the next call sees the full conversation."""
    history.append(HumanMessage(user_text))
    answer = model.invoke(history)
    history.append(answer)
    return answer.text


def main() -> None:
    model = get_chat_model(
        fake_responses=[
            "Nice to meet you, Ana! Kubernetes is a great topic for a DevOps engineer.",
            "Your name is Ana.",
        ]
    )

    # The system message sets the rules for the whole conversation.
    history: list[BaseMessage] = [SystemMessage("You are a concise assistant for DevOps engineers.")]

    print("Bot:", chat(model, history, "Hi, my name is Ana and I'm studying Kubernetes."))
    # This only works because the first exchange is still in `history`:
    # chat models are stateless, like a person with no short-term memory
    # who re-reads the whole chat log before every reply.
    print("Bot:", chat(model, history, "What is my name?"))

    print("\nHistory sent on the last call:")
    for message in history:
        role = "AI" if isinstance(message, AIMessage) else type(message).__name__
        print(f"  {role}: {message.text}")


if __name__ == "__main__":
    main()
