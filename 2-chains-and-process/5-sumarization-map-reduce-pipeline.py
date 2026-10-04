"""Map-reduce summarization built with LCEL (no legacy load_summarize_chain).

Run: uv run python 2-chains-and-process/5-sumarization-map-reduce-pipeline.py
"""

from dotenv import load_dotenv
from langchain_core.globals import set_debug
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

from learning_langchain.cli import ask, ask_yes_no
from learning_langchain.models import get_chat_model

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

FALLBACK_TOPIC = "the FIFA World Cup 2026"

# Prompt used only when the user does not type anything, so we always have
# real content to summarize.
fallback_template = PromptTemplate(
    input_variables=["topic"],
    template="Write a short, informative paragraph (4-6 sentences) about {topic}.",
)

# ---- MAP step ----
# Prompt template used to summarize each individual document on its own.
map_template = PromptTemplate(
    input_variables=["document"],
    template="Summarize the following text in 2 concise sentences:\n\n{document}",
)

# ---- REDUCE step ----
# Prompt template used to combine all the partial (map) summaries into a
# single, coherent final summary.
reduce_template = PromptTemplate(
    input_variables=["summaries"],
    template=(
        "The following are summaries of several texts:\n\n{summaries}\n\n"
        "Combine them into a single, coherent final summary."
    ),
)


def format_summaries(summaries: list) -> dict:
    """Join the list of partial (map) summaries into one string, so it can be
    fed as a single input variable to the reduce prompt."""
    joined = "\n\n".join(f"- {s}" for s in summaries)
    return {"summaries": joined}


def build_pipeline(model: BaseChatModel) -> Runnable:
    """Full map-reduce pipeline, built with LCEL ("|" pipe operator):
    1) map_runnable: summarizes each document individually (map)
    2) format_runnable: formats the partial summaries into one reduce input
    3) reduce_template | model: combines all partial summaries into one (reduce)

    Analogy: several people each summarize one chapter (map), then an
    editor merges their notes into the book's summary (reduce).
    """
    map_chain = map_template | model

    def map_documents(docs: list) -> list:
        """MAP step of map-reduce: summarize each document independently,
        producing one partial summary per input document."""
        return [map_chain.invoke({"document": doc}).text.strip() for doc in docs]

    return RunnableLambda(map_documents) | RunnableLambda(format_summaries) | reduce_template | model


def read_document(model: BaseChatModel, order: str) -> str:
    """Ask the user for a text; if ENTER is pressed (empty input), auto-generate
    a paragraph about the FIFA World Cup 2026 instead, using the LLM itself."""
    text = ask(f"Enter the {order} text to summarize", "")
    if text:
        return text
    generated = (fallback_template | model).invoke({"topic": FALLBACK_TOPIC})
    return generated.text.strip()


def main() -> None:
    # set_debug(True) turns on LangChain's global debug tracing: it prints
    # every step of the pipeline (chain/start, llm/start, llm/end, ...) to
    # the console. set_verbose() has no visible effect on LCEL pipelines.
    set_debug(ask_yes_no("Enable debug mode (prints every step)?", default=False))

    model = get_chat_model(
        fake_responses=[
            "The 2026 FIFA World Cup is hosted by Canada, Mexico and the United States.",
            "It is the first edition with 48 teams.",
        ]
    )

    # Collect the 3 source documents dynamically from user input (or auto-generated).
    documents = [read_document(model, order) for order in ("first", "second", "third")]
    final_summary = build_pipeline(model).invoke(documents)

    print("\n=== FINAL SUMMARY ===")
    print(final_summary.text.strip())


if __name__ == "__main__":
    main()
