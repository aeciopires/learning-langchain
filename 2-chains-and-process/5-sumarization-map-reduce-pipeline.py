from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from langchain_core.globals import set_debug
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# set_debug(True) turns on LangChain's global debug tracing. Unlike
# set_verbose, it prints every step of the pipeline (chain/start, prompt
# input, llm/start, llm/end, tokens, etc.) directly to the console, which is
# exactly what we want to visualize how the LLM is invoked at each stage of
# the map-reduce summarization below.
set_debug(True)

# Chat model (Google GenAI / Gemini) used both to auto-generate fallback text
# and to run the map and reduce summarization steps.
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

FALLBACK_TOPIC = "the FIFA World Cup 2026"

# Prompt used only when the user does not type anything, so we always have
# real content to summarize.
fallback_template = PromptTemplate(
    input_variables=["topic"],
    template="Write a short, informative paragraph (4-6 sentences) about {topic}.",
)
fallback_chain = fallback_template | model


def read_document(order: str) -> str:
    """Ask the user for a text; if ENTER is pressed (empty input), auto-generate
    a paragraph about the FIFA World Cup 2026 instead, using the LLM itself."""
    text = input(
        f"Enter the {order} text to summarize "
        "(press ENTER to auto-generate a text about the FIFA World Cup 2026): "
    ).strip()
    if text:
        return text
    generated = fallback_chain.invoke({"topic": FALLBACK_TOPIC})
    return generated.content.strip()


# Collect the 3 source documents dynamically from user input (or auto-generated).
documents = [read_document(order) for order in ("first", "second", "third")]

# ---- MAP step ----
# Prompt template used to summarize each individual document on its own.
map_template = PromptTemplate(
    input_variables=["document"],
    template="Summarize the following text in 2 concise sentences:\n\n{document}",
)
map_chain = map_template | model


def map_documents(docs: list) -> list:
    """MAP step of map-reduce: summarize each document independently,
    producing one partial summary per input document."""
    return [map_chain.invoke({"document": doc}).content.strip() for doc in docs]


map_runnable = RunnableLambda(map_documents)

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
reduce_chain = reduce_template | model


def format_summaries(summaries: list) -> dict:
    """Join the list of partial (map) summaries into one string, so it can be
    fed as a single input variable to the reduce prompt."""
    joined = "\n\n".join(f"- {s}" for s in summaries)
    return {"summaries": joined}


format_runnable = RunnableLambda(format_summaries)

# Full map-reduce pipeline, built with LCEL ("|" pipe operator):
# 1) map_runnable: summarizes each of the 3 documents individually (map)
# 2) format_runnable: formats the 3 partial summaries into one reduce input
# 3) reduce_chain: combines all partial summaries into one final summary (reduce)
pipeline = map_runnable | format_runnable | reduce_chain

final_summary = pipeline.invoke(documents)

print("\n=== FINAL SUMMARY ===")
print(final_summary.content.strip())
