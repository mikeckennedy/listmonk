"""Guard the type-clean state of the tree.

ty is the authoritative type checker for this repo (see ty.toml). This test runs it
and fails on any diagnostic, so a regression shows up in the normal test run rather
than the next time someone happens to check by hand. It takes well under a second.

ty is a dev dependency (`pip install -e .[dev]`); when it isn't installed the test
skips rather than fails, so the suite still runs on a bare install.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _find_ty() -> str | None:
    """Locate the ty binary, preferring the project's venv over whatever is on PATH."""
    for candidate in (REPO_ROOT / 'venv' / 'bin' / 'ty', REPO_ROOT / 'venv' / 'Scripts' / 'ty.exe'):
        if candidate.exists():
            return str(candidate)
    return shutil.which('ty')


def test_ty_reports_no_diagnostics():
    ty = _find_ty()
    if ty is None:
        pytest.skip('ty is not installed; run `pip install -e .[dev]` to enable the type-check gate')

    result = subprocess.run(
        [ty, 'check', '--output-format', 'concise'],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f'ty reported type diagnostics (exit {result.returncode}). Fix them, or add a\n'
        f'`# ty: ignore[rule]` with a one-line justification if it is a checker limitation.\n\n'
        f'{result.stdout}{result.stderr}'
    )
