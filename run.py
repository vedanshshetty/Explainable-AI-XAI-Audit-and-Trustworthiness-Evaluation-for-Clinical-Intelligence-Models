"""Run both backend and frontend."""
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_server(name, cmd, ready_check):
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env={**__import__("os").environ},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in proc.stdout:
        sys.stdout.write(line.decode(errors="replace"))
        sys.stdout.flush()
        if ready_check(line.decode(errors="replace")):
            break


def check_backend(line):
    return "Application startup complete" in line or "Uvicorn running" in line


def check_frontend(line):
    return "Running on" in line or "streamlit" in line.lower()


if __name__ == "__main__":
    import os
    os.chdir(str(ROOT))

    print("Starting Clinical Intelligence System...")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:8501")
    print("-" * 40)

    t1 = threading.Thread(target=run_server, args=("backend", [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], check_backend), daemon=True)
    t2 = threading.Thread(target=run_server, args=("frontend", [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"], check_frontend), daemon=True)

    t1.start()
    t2.start()

    print("Servers starting in background. Press Ctrl+C to stop.")
    try:
        while t1.is_alive() or t2.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
