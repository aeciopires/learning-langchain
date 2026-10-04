"""Step 4: agentic RAG - the retriever becomes a tool the agent decides to call.

Run: uv run python 4-rag/4-rag-agent.py
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.vectorstores import VectorStore

from learning_langchain.cli import ask
from learning_langchain.models import get_chat_model, get_embeddings
from learning_langchain.rag import (
    build_vector_store,
    format_documents,
    load_markdown_documents,
    split_documents,
)

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def build_agent(vector_store: VectorStore, model: BaseChatModel):
    """Unlike the fixed chain in 3-rag-chain.py (always retrieve, then answer),
    the agent decides IF and WHAT to search - it may rewrite the question,
    search twice, or skip searching for a greeting."""

    @tool
    def search_runbooks(query: str) -> str:
        """Search the operational runbooks and return the most relevant passages."""
        return format_documents(vector_store.similarity_search(query, k=3))

    return create_agent(
        model=model,
        tools=[search_runbooks],
        system_prompt=(
            "You are an on-call assistant. Search the runbooks before answering "
            "operational questions, and cite the source file of each step."
        ),
    )


FAKE_RESPONSES: list[str | AIMessage] = [
    AIMessage(
        content="",
        tool_calls=[
            {"name": "search_runbooks", "args": {"query": "TLS certificate expiring"}, "id": "call_1"}
        ],
    ),
    "(fake) Trigger a manual renewal; if it fails, open a ticket with the security team "
    "[source: certificate-expiry.md].",
]


def main() -> None:
    vector_store = build_vector_store(split_documents(load_markdown_documents()), get_embeddings())
    agent = build_agent(vector_store, get_chat_model(fake_responses=FAKE_RESPONSES, temperature=0))

    question = ask("Ask the on-call assistant", "A TLS certificate expires in 10 days. What now?")
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            print("Agent called:", [(c["name"], c["args"]) for c in message.tool_calls])
    print("\nAnswer:", result["messages"][-1].text)


if __name__ == "__main__":
    main()
