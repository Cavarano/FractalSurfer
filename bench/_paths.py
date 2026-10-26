"""Make the project's `src/` directory importable.

Imported for its side effect - keeps `sys.path` munging out of every other module.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"

if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

REPO_ROOT = _REPO_ROOT
SRC = _SRC
