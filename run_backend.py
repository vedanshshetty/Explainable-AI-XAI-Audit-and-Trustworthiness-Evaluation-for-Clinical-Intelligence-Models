"""Start the API server from anywhere.

`python -m uvicorn backend.main:app` fails with
`ModuleNotFoundError: No module named 'backend'` whenever the terminal is sitting
in a directory other than the project root, because the reloader inherits that
directory. This wrapper pins the working directory and PYTHONPATH first.

Usage:
    python run_backend.py            # normal
    python run_backend.py --reload   # auto-reload during development
    python run_backend.py --port 8080
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    argv = sys.argv[1:]
    port = "8000"
    if "--port" in argv:
        index = argv.index("--port")
        if index + 1 < len(argv):
            port = argv[index + 1]
    reload_flag = "--reload" in argv

    if not (ROOT / "backend" / "main.py").exists():
        print(f"ERROR: backend/main.py not found under {ROOT}", file=sys.stderr)
        return 1

    env = {**os.environ}
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{existing}" if existing else str(ROOT)

    cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1", "--port", port,
    ]
    if reload_flag:
        cmd.append("--reload")

    print(f"Starting backend from {ROOT} on port {port}")
    return subprocess.call(cmd, cwd=str(ROOT), env=env)


if __name__ == "__main__":
    sys.exit(main())