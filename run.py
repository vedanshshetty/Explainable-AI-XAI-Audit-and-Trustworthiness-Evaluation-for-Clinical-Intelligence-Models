"""Run the backend and frontend.

Works no matter which directory you invoke this from. The script pins its own
project root as the working directory and puts it on PYTHONPATH, so the common
`ModuleNotFoundError: No module named 'backend'` never happens again - even if
the terminal is sitting in backend/ or in the parent folder.
"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# The project root is the folder containing run.py.
ROOT = Path(__file__).resolve().parent


def child_env() -> dict:
    env = {**os.environ}
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{existing}" if existing else str(ROOT)
    env["PYTHONUNBUFFERED"] = "1"
    return env


def stream(name: str, cmd: list, ready_check) -> None:
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),            # the important part: never inherit the caller's cwd
        env=child_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )
    ready = False
    try:
        for line in proc.stdout:
            sys.stdout.write(f"[{name}] {line}")
            sys.stdout.flush()
            if not ready and ready_check(line):
                ready = True
    except Exception:
        pass
    finally:
        if proc.poll() is not None and not ready:
            print(
                f"[{name}] exited before becoming ready (code {proc.returncode}). "
                "See the output above for the cause.",
                flush=True,
            )


def backend_ready(line: str) -> bool:
    return "Application startup complete" in line or "Uvicorn running on" in line


def frontend_ready(line: str) -> bool:
    low = line.lower()
    return "you can now view your streamlit app" in low or "local url:" in low


if __name__ == "__main__":
    os.chdir(str(ROOT))

    print("Clinical Intelligence System")
    print(f"  python   : {sys.executable}")
    print(f"  project  : {ROOT}")
    print(f"  backend  : http://localhost:8000")
    print(f"  frontend : http://localhost:8501")
    print("-" * 58)

    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1", "--port", "8000",
    ]
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501",
    ]

    threads = [
        threading.Thread(target=stream, args=("backend", backend_cmd, backend_ready), daemon=True),
        threading.Thread(target=stream, args=("frontend", frontend_cmd, frontend_ready), daemon=True),
    ]
    for t in threads:
        t.start()

    print("Starting. Press Ctrl+C to stop.")
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping.")
        sys.exit(0)