"""Structured output: ask the model to fill a Pydantic schema instead of free text.

Run: uv run python 2-chains-and-process/7-structured-output.py
"""

from typing import Literal

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field

from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


class Incident(BaseModel):
    """An incident extracted from an alert message."""

    # Field descriptions are sent to the model: they are part of the prompt.
    service: str = Field(description="Name of the affected service")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Incident severity")
    summary: str = Field(description="One-sentence summary of the problem")
    needs_rollback: bool = Field(description="True if the alert suggests rolling back a deployment")


prompt = ChatPromptTemplate(
    [
        ("system", "You are an SRE assistant. Extract the incident data from the alert."),
        ("user", "{alert}"),
    ]
)


def build_chain(model: BaseChatModel) -> Runnable:
    """with_structured_output(Incident) makes the model answer with data that
    is validated into an Incident object - like a form with mandatory fields
    instead of a blank sheet of paper."""
    return prompt | model.with_structured_output(Incident)


# Offline mode: providers return structured output as a tool call named after
# the schema; the fake model reproduces that answer.
FAKE_STRUCTURED_ANSWER = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "Incident",
            "args": {
                "service": "checkout-api",
                "severity": "high",
                "summary": "Error rate above 20% right after deploy v2.3.1.",
                "needs_rollback": True,
            },
            "id": "call_incident_1",
        }
    ],
)


def main() -> None:
    model = get_chat_model(fake_responses=[FAKE_STRUCTURED_ANSWER])
    alert = (
        "ALERT: checkout-api 5xx error rate is 23% for 10 minutes, "
        "starting right after deploy v2.3.1 at 14:02 UTC."
    )
    incident = build_chain(model).invoke({"alert": alert})

    # The result is a real Python object: attributes, types and validation.
    print(type(incident).__name__, "->", incident)
    if incident.needs_rollback:
        print(f"Action: roll back {incident.service} (severity: {incident.severity})")


if __name__ == "__main__":
    main()
