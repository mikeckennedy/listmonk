#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed repo-root docs/ folder.

Great Docs writes its output to ./great-docs/_site/, which is ephemeral (the build dir
self-ignores via its own .gitignore and is regenerated each build). The site we actually
publish lives in a committed repo-root docs/ folder that the server serves via nginx after
a `git pull`. This script runs the build and then fully replaces docs/ with the fresh
_site/ so the two never drift.

Run it with the project's venv Python:  ./venv/bin/python scripts/build_docs.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
PKG_DIR = _SCRIPTS.parent  # dir with pyproject.toml + great-docs.yml — also the git root here
REPO_ROOT = PKG_DIR  # the package lives at the git root, so docs/ is committed alongside it
SITE = PKG_DIR / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'


def main() -> int:
    # Prefer the great-docs next to the Python running this script (the venv), so the
    # build uses the same interpreter where `listmonk` is importable for introspection.
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=PKG_DIR).returncode != 0:
        return 1

    if not SITE.is_dir():
        print(f'build output missing: {SITE}', file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)
    print(f'Mirrored -> {DEST} ({sum(1 for p in DEST.rglob("*") if p.is_file())} files)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
