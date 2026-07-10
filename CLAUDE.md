# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A personal learning repository for LangChain in Python (GPL-3.0 licensed). It is not a package or service — it's a collection of small, standalone, runnable scripts organized progressively by topic. There is no test suite, linter config, or build system.

## Setup and running scripts

```bash
# Create and activate the virtualenv (already exists as ./venv in this repo)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (Google AI Studio and/or OpenAI)
cp .env.example .env
# then fill GOOGLE_API_KEY / OPENAI_API_KEY in .env

# Run any example script directly
python DIR_NAME/FILE_NAME.py
# e.g.
python 2-chains-and-process/5-sumarization-map-reduce-pipeline.py
```

Some scripts are interactive and call `input()` — when running them non-interactively (e.g. testing from an agent), pipe newline-separated answers via stdin: `printf "\n\n\n" | python DIR/FILE.py`. Pressing ENTER on these prompts always falls back to a documented default (a specific value, or the repository base directory).

There are no automated tests, linters, or CI configured in this repo.

## Repository structure

Directories are numbered learning modules; files within each are numbered in the order they should be read/run, each building on concepts from the previous one:

- `1-fundamentals/` — basic model initialization (`ChatOpenAI`, `init_chat_model`, `ChatGoogleGenerativeAI`) and prompt templates (`PromptTemplate`, `ChatPromptTemplate`).
- `2-chains-and-process/` — LCEL (`|` pipe) chains: basic chains, the `@chain` decorator, `RunnableLambda`, dynamic multi-variable prompts, and a manual map-reduce summarization pipeline.
- `3-tools-and-agents/` — tool-calling agents built with `langchain.agents.create_agent` (LangGraph-backed under the hood) and custom `@tool`-decorated functions.

When adding a new example, follow the existing numbering convention and put it in the module directory it conceptually belongs to (create a new numbered directory for a genuinely new topic).

## Key library facts specific to this codebase

The installed stack is **LangChain 1.x** (`langchain==1.3.11`, `langchain-core==1.4.8`), which is a major-version rewrite. Do not assume APIs from pre-1.0 LangChain tutorials/blog posts work here:

- `langchain.chains` (legacy `Chain` classes, e.g. `load_summarize_chain`) **does not exist** in this version. Build pipelines with LCEL (`prompt | model`, `RunnableLambda`, `@chain`) instead — see `2-chains-and-process/5-sumarization-map-reduce-pipeline.py` for a manual map-reduce implementation done this way.
- Agents are built with `langchain.agents.create_agent(model, tools, system_prompt=...)`, which returns a compiled LangGraph state graph. Invoke it with `agent.invoke({"messages": [...]})` and read the reply from `result["messages"][-1]`.
- `langchain_core.globals.set_verbose(True)` has **no visible effect** on LCEL/agent pipelines in this version. Use `langchain_core.globals.set_debug(True)` instead — it prints `chain/start`, `llm/start`, `llm/end`, etc. to the console and is what "verbose mode" means throughout this repo.
- Chat model responses (`AIMessage.content`) from `ChatGoogleGenerativeAI` may come back as either a plain `str` or a list of content blocks (e.g. `[{"type": "text", "text": "..."}]` plus non-text "extras" like thought signatures). Don't assume `.content` is always a string — normalize it first (see `extract_text()` in `3-tools-and-agents/1-agent-review.py`).
- To enumerate available Gemini models at runtime, use the `google-genai` SDK directly: `from google import genai; genai.Client().models.list()`, filtering by `"generateContent" in model.supported_actions`. `genai.Client()` picks up `GOOGLE_API_KEY` from the environment automatically once `load_dotenv()` has run.

## Conventions used across scripts

- Every script starts with `from dotenv import load_dotenv` followed by `load_dotenv()`.
- Google Gemini (`langchain_google_genai.ChatGoogleGenerativeAI`) is the default/primary model provider used across examples, even though `.env.example` also has an `OPENAI_API_KEY` slot for the occasional OpenAI-based example. The conventional default model name is `"gemini-2.5-flash"`.
- Interactive scripts prompt with `input()` and use an "ENTER = default" pattern (e.g. empty temperature falls back to `0.5`, empty directory falls back to the repo root via `Path(__file__).resolve().parent.parent`).
- Comments in code explain the *objective* of each step (what a `RunnableLambda`/prompt/tool does and why), matching the teaching purpose of this repo — keep this style when adding new examples rather than leaving code uncommented.
