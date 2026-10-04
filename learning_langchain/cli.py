"""Small helpers for the interactive examples (the "ENTER = default" pattern)."""

from __future__ import annotations


def ask(prompt: str, default: str) -> str:
    """Ask the user a question; ENTER (or no stdin at all) returns `default`.

    EOFError is raised by input() when stdin is closed or empty - e.g. when a
    script runs from `make run-all` or a test - so it also means "use the
    default" instead of crashing.
    """
    try:
        answer = input(f"{prompt} (ENTER = {default!r}): ").strip()
    except EOFError:
        print()
        return default
    return answer or default


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask a y/N question; ENTER (or no stdin) returns `default`."""
    answer = ask(f"{prompt} [y/n]", "y" if default else "n").lower()
    return answer in ("y", "yes", "s", "sim")
