"""Helpers shared by the unit tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_script(relative_path: str) -> ModuleType:
    """Import an example script by its file path.

    The example scripts live in directories such as "2-chains-and-process"
    and are named like "3-runnable-lambda.py" - neither is a valid Python
    identifier, so `import` can't reach them. importlib loads the file
    directly; `if __name__ == "__main__":` keeps main() from running.
    """
    path = REPO_ROOT / relative_path
    module_name = "script_" + path.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def echo_model() -> RunnableLambda:
    """A stand-in for a chat model that answers with the full prompt it got.

    Useful to assert WHAT a chain sends to the model (the rendered prompt),
    which a fake model with canned answers can't show.
    """
    return RunnableLambda(lambda prompt_value: AIMessage(content=prompt_value.to_string()))
