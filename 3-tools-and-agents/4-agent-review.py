"""A code review agent that discovers and reads Python files with its tools.

Run: uv run python 3-tools-and-agents/4-agent-review.py
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.globals import set_debug
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage

from learning_langchain.cli import ask, ask_yes_no
from learning_langchain.config import load_settings
from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

# Base directory of this repository (parent of "3-tools-and-agents"), used as
# the default review target when the user presses ENTER without typing a directory.
REPO_BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_TEMPERATURE = 0.2


def list_available_models() -> list[str]:
    """Query the Google GenAI API and return the names of all models that
    support text generation ("generateContent"), so the user can pick one."""
    from google import genai

    client = genai.Client()
    return sorted(
        (m.name or "").removeprefix("models/")
        for m in client.models.list()
        if "generateContent" in (m.supported_actions or [])
    )


def parse_temperature(raw_value: str) -> float:
    """Convert the typed temperature; an invalid number falls back to DEFAULT_TEMPERATURE."""
    try:
        return float(raw_value)
    except ValueError:
        print(f"Invalid temperature '{raw_value}', using default {DEFAULT_TEMPERATURE}.")
        return DEFAULT_TEMPERATURE


# Tool #1: lets the agent discover which Python files exist inside the
# directory it needs to review, instead of us hardcoding the file list.
@tool
def list_python_files(directory: str) -> str:
    """List all Python (.py) files found recursively inside the given directory."""
    base = Path(directory).expanduser()
    if not base.exists():
        return f"Directory not found: {directory}"
    files = sorted(str(p) for p in base.rglob("*.py") if ".venv" not in p.parts)
    return "\n".join(files) if files else "No Python files found in this directory."


# Tool #2: lets the agent read the content of a specific file it picked from
# the list above, so it can actually analyze the code.
@tool
def read_file_content(file_path: str) -> str:
    """Read and return the text content of a single file, given its path."""
    path = Path(file_path).expanduser()
    if not path.exists() or not path.is_file():
        return f"File not found: {file_path}"
    return path.read_text(encoding="utf-8", errors="ignore")


# System prompt that defines the agent's role and how it should use its tools.
SYSTEM_PROMPT = (
    "You are a senior software engineer specialized in reviewing LangChain "
    "Python code. First call the 'list_python_files' tool to discover the "
    ".py files inside the directory the user gives you. Then call "
    "'read_file_content' to read each file relevant to LangChain usage. "
    "Review the code for correctness, LangChain best practices, readability "
    "and potential bugs. Produce a concise, well-structured code review, "
    "organized by file."
)


def build_agent(model: BaseChatModel):
    """The agent itself: a model + a set of tools + a system prompt, wired
    together by create_agent() into a tool-calling loop (LangGraph state
    graph under the hood) that decides which tool to call and when to stop."""
    return create_agent(
        model=model, tools=[list_python_files, read_file_content], system_prompt=SYSTEM_PROMPT
    )


def fake_responses(directory: str) -> list:
    """Offline mode: list the files, read this script, then answer."""
    return [
        AIMessage(
            content="",
            tool_calls=[{"name": "list_python_files", "args": {"directory": directory}, "id": "call_1"}],
        ),
        AIMessage(
            content="",
            tool_calls=[{"name": "read_file_content", "args": {"file_path": __file__}, "id": "call_2"}],
        ),
        "(fake review) 4-agent-review.py: tools have clear docstrings; consider limiting file size.",
    ]


def main() -> None:
    settings = load_settings()
    if settings.provider == "google_genai":
        # Show every model the API key can use, so the user can pick one.
        print("Models supported by Google GenAI (generateContent):")
        for name in list_available_models():
            print(f"  - {name}")
    model_name = ask("Enter the model to use", settings.model)
    temperature = parse_temperature(ask("Enter the temperature", str(DEFAULT_TEMPERATURE)))
    target_directory = ask("Enter the directory to review", str(REPO_BASE_DIR))

    # set_debug prints every step of the agent's tool-calling loop (model calls,
    # tool calls, tool outputs) to the console, which is what "verbose mode"
    # means here: it shows how the agent reasons and reviews the code internally.
    set_debug(ask_yes_no("Enable verbose mode?", default=False))

    model = get_chat_model(
        fake_responses=fake_responses(target_directory), model_name=model_name, temperature=temperature
    )
    request = f"Please review the LangChain Python code inside this directory: {target_directory}"
    result = build_agent(model).invoke({"messages": [{"role": "user", "content": request}]})

    print("\n=== CODE REVIEW ===")
    print(result["messages"][-1].text)


if __name__ == "__main__":
    main()
