from pathlib import Path

from google import genai
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.globals import set_debug
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of this repository (parent of "3-tools-and-agents"), used as
# the default review target when the user presses ENTER without typing a directory.
REPO_BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.2


def list_available_models() -> list:
    """Query the Google GenAI API and return the names of all models that
    support text generation ("generateContent"), so the user can pick one."""
    client = genai.Client()
    return sorted(
        m.name.removeprefix("models/")
        for m in client.models.list()
        if "generateContent" in (m.supported_actions or [])
    )


def ask_model() -> str:
    """Show every LLM supported by Google GenAI and ask the user which one to
    use; ENTER falls back to DEFAULT_MODEL."""
    print("Models supported by Google GenAI (generateContent):")
    for name in list_available_models():
        print(f"  - {name}")
    chosen = input(f"Enter the model to use (press ENTER for default '{DEFAULT_MODEL}'): ").strip()
    return chosen or DEFAULT_MODEL


def ask_temperature() -> float:
    """Ask the user for the sampling temperature; ENTER (or an invalid
    number) falls back to DEFAULT_TEMPERATURE."""
    raw_value = input(f"Enter the temperature (press ENTER for default {DEFAULT_TEMPERATURE}): ").strip()
    if not raw_value:
        return DEFAULT_TEMPERATURE
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
    files = sorted(str(p) for p in base.rglob("*.py"))
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


# Chat model (Google GenAI / Gemini) that acts as the code review agent's
# brain. Both "model" (the model name) and "temperature" are chosen
# dynamically by the user below; a low temperature is recommended to keep
# the review focused and deterministic.
model = ask_model()
temperature = ask_temperature()
llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)

# System prompt that defines the agent's role and how it should use its tools.
system_prompt = (
    "You are a senior software engineer specialized in reviewing LangChain "
    "Python code. First call the 'list_python_files' tool to discover the "
    ".py files inside the directory the user gives you. Then call "
    "'read_file_content' to read each file relevant to LangChain usage. "
    "Review the code for correctness, LangChain best practices, readability "
    "and potential bugs. Produce a concise, well-structured code review, "
    "organized by file."
)

# The agent itself: a model + a set of tools + a system prompt, wired
# together by create_agent() into a tool-calling loop (LangGraph state
# graph under the hood) that decides which tool to call and when to stop.
agent = create_agent(
    model=llm,
    tools=[list_python_files, read_file_content],
    system_prompt=system_prompt,
)


def ask_directory() -> str:
    """Ask the user which directory to review; ENTER falls back to this repository's base directory."""
    directory = input(
        f"Enter the directory to review (press ENTER to use the repository base directory: {REPO_BASE_DIR}): "
    ).strip()
    return directory or str(REPO_BASE_DIR)


def ask_verbose_mode() -> bool:
    """Ask the user whether to enable verbose mode; ENTER disables it."""
    answer = input("Enable verbose mode? (y/N, press ENTER to disable): ").strip().lower()
    return answer == "y"


target_directory = ask_directory()
verbose_enabled = ask_verbose_mode()

# set_debug prints every step of the agent's tool-calling loop (model calls,
# tool calls, tool outputs) to the console, which is what "verbose mode"
# means here: it shows how the agent reasons and reviews the code internally.
set_debug(verbose_enabled)

def extract_text(content) -> str:
    """Normalize a message's content into plain text.

    Gemini responses may come either as a plain string or as a list of
    content blocks (e.g. [{"type": "text", "text": "..."}]), so this
    extracts only the readable text, ignoring non-text extras."""
    if isinstance(content, str):
        return content
    return "\n".join(
        block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
    )


result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": f"Please review the LangChain Python code inside this directory: {target_directory}",
            }
        ]
    }
)

print("\n=== CODE REVIEW ===")
print(extract_text(result["messages"][-1].content))
