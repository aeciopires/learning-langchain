"""Tools: Python functions a model can ask to run. No model needed here.

Run: uv run python 3-tools-and-agents/1-first-tool.py
"""

import shutil
from pathlib import Path

from langchain.tools import tool


# @tool turns a function into a tool. The function name becomes the tool
# name, the docstring becomes its description and the type hints become its
# input schema. The model reads all three to decide WHEN and HOW to call it,
# so a clear docstring is as important as the code.
@tool
def check_disk_usage(path: str = "/") -> str:
    """Return the total, used and free disk space (in GiB) of the filesystem holding `path`."""
    target = Path(path).expanduser()
    if not target.exists():
        return f"Path not found: {path}"
    usage = shutil.disk_usage(target)
    gib = 1024**3
    percent_used = usage.used / usage.total * 100
    return (
        f"{target}: total={usage.total / gib:.1f} GiB, used={usage.used / gib:.1f} GiB "
        f"({percent_used:.0f}%), free={usage.free / gib:.1f} GiB"
    )


def main() -> None:
    # What the model "sees" about the tool:
    print("Name:       ", check_disk_usage.name)
    print("Description:", check_disk_usage.description)
    print("Arguments:  ", check_disk_usage.args)

    # A tool is also a Runnable: you can call it yourself with invoke() and a
    # dict of arguments - exactly what an agent does when the model asks for it.
    print("Result:     ", check_disk_usage.invoke({"path": "/"}))
    print("Bad path:   ", check_disk_usage.invoke({"path": "/does/not/exist"}))


if __name__ == "__main__":
    main()
