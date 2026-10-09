"""Backend package.

Keeps the absolute imports used throughout the backend working regardless of the
directory the process was launched from.
"""

import sys
from pathlib import Path

# Project root is the parent of this package directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))