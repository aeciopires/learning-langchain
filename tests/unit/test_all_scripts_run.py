"""Smoke test: every example script's main() runs offline, with every
interactive question answered by its default - the same as `make run-all`."""

from pathlib import Path

import pytest

from tests._helpers import REPO_ROOT, load_script

MODULE_DIRS = ["1-fundamentals", "2-chains-and-process", "3-tools-and-agents", "4-rag"]
SCRIPTS = sorted(str(p.relative_to(REPO_ROOT)) for d in MODULE_DIRS for p in (REPO_ROOT / d).glob("*.py"))


def test_every_module_has_scripts():
    assert len(SCRIPTS) >= 20


@pytest.mark.parametrize("relative_path", SCRIPTS)
def test_script_main_runs_offline(relative_path, no_stdin, capsys):
    load_script(relative_path).main()
    assert capsys.readouterr().out.strip(), f"{Path(relative_path).name} printed nothing"
