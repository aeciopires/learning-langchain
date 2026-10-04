"""A first agent: a model that decides which tools to call, in a loop.

Run: uv run python 3-tools-and-agents/2-simple-agent.py
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage

from learning_langchain.cli import ask
from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

# A tiny, hardcoded "inventory" standing in for a real monitoring API, so the
# example is safe to run anywhere. In real life this would call Prometheus,
# the Kubernetes API, a CMDB, etc.
SERVICES = {
    "checkout-api": {"status": "degraded", "replicas": "2/3", "version": "v2.3.1"},
    "payments-api": {"status": "healthy", "replicas": "3/3", "version": "v1.8.0"},
    "auth-api": {"status": "healthy", "replicas": "2/2", "version": "v4.0.2"},
}


@tool
def list_services() -> str:
    """List the names of every service being monitored."""
    return ", ".join(sorted(SERVICES))


@tool
def get_service_status(service: str) -> str:
    """Get the status, ready replicas and deployed version of one service."""
    info = SERVICES.get(service)
    if info is None:
        return f"Unknown service '{service}'. Known services: {', '.join(sorted(SERVICES))}"
    return f"{service}: status={info['status']}, replicas={info['replicas']}, version={info['version']}"


SYSTEM_PROMPT = (
    "You are an on-call SRE assistant. Use the tools to check services before "
    "answering. Be concise and say which service needs attention, if any."
)

# Offline mode: the fake model "decides" to call list_services, then
# get_service_status, then answers - the same loop a real model would run.
FAKE_RESPONSES: list[str | AIMessage] = [
    AIMessage(content="", tool_calls=[{"name": "list_services", "args": {}, "id": "call_1"}]),
    AIMessage(
        content="",
        tool_calls=[{"name": "get_service_status", "args": {"service": "checkout-api"}, "id": "call_2"}],
    ),
    "checkout-api is degraded (2/3 replicas ready, version v2.3.1); the other services are healthy.",
]


def build_agent(model: BaseChatModel):
    """create_agent() wires a model, tools and a system prompt into a loop
    (a LangGraph graph): model -> tool calls -> tool results -> model ...
    until the model answers without asking for a tool."""
    return create_agent(model=model, tools=[list_services, get_service_status], system_prompt=SYSTEM_PROMPT)


def main() -> None:
    question = ask("Ask the on-call assistant", "Is any service unhealthy right now?")
    agent = build_agent(get_chat_model(fake_responses=FAKE_RESPONSES, temperature=0))
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # result["messages"] holds the whole loop: the question, every tool call,
    # every tool result and the final answer (the last message).
    print("\n=== Agent steps ===")
    for message in result["messages"]:
        tool_calls = getattr(message, "tool_calls", None)
        detail = f"tool_calls={[call['name'] for call in tool_calls]}" if tool_calls else message.text
        print(f"{type(message).__name__}: {detail}")

    print("\n=== Final answer ===")
    print(result["messages"][-1].text)


if __name__ == "__main__":
    main()
