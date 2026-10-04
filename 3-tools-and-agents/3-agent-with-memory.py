"""Short-term memory: a checkpointer lets the agent remember a conversation.

Run: uv run python 3-tools-and-agents/3-agent-with-memory.py
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def build_agent(model: BaseChatModel):
    """InMemorySaver stores each conversation's messages in RAM, keyed by
    thread_id - like a notebook with one page per customer. It is lost when
    the program exits; production code uses a persistent checkpointer
    (e.g. PostgresSaver from langgraph-checkpoint-postgres)."""
    return create_agent(
        model=model,
        tools=[],
        system_prompt="You are a friendly assistant. Keep answers short.",
        checkpointer=InMemorySaver(),
    )


def ask_agent(agent, thread_id: str, text: str) -> str:
    """Send one message in a given conversation (thread) and return the reply.
    Only the NEW message is sent: the checkpointer adds the history."""
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [{"role": "user", "content": text}]}, config=config)
    return result["messages"][-1].text


def main() -> None:
    model = get_chat_model(
        fake_responses=[
            "Nice to meet you, Bruno!",
            "Your name is Bruno and you work with Terraform.",
            "I don't know your name yet - this is a new conversation.",
        ]
    )
    agent = build_agent(model)

    print("[thread-1] Bot:", ask_agent(agent, "thread-1", "Hi! I'm Bruno and I work with Terraform."))
    print("[thread-1] Bot:", ask_agent(agent, "thread-1", "What's my name and what do I work with?"))
    # A different thread_id is a different conversation, with no shared memory.
    print("[thread-2] Bot:", ask_agent(agent, "thread-2", "What's my name?"))


if __name__ == "__main__":
    main()
