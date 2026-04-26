"""Unified local runner for the project stacks.

Usage examples:
  python3 scripts/run_project.py streamlit
  python3 scripts/run_project.py backend
  python3 scripts/run_project.py frontend
  python3 scripts/run_project.py platform
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "platform" / "backend"
FRONTEND_DIR = ROOT / "platform" / "frontend"


def _backend_cmd(reload: bool) -> list[str]:
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
    if reload:
        cmd.append("--reload")
    return cmd


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _run_blocking(cmd: list[str], cwd: Path) -> int:
    process = subprocess.run(cmd, cwd=str(cwd))
    return int(process.returncode)


def _spawn(cmd: list[str], cwd: Path) -> subprocess.Popen:
    return subprocess.Popen(cmd, cwd=str(cwd))


def _run_platform_dual() -> int:
    if not _module_available("uvicorn"):
        print("Missing dependency: uvicorn")
        print(f"Install with: {sys.executable} -m pip install -r platform/backend/requirements.txt")
        return 1

    # In dual-mode we prefer stability over hot-reload. Frontend already has HMR.
    backend = _spawn(_backend_cmd(reload=False), BACKEND_DIR)
    time.sleep(1.2)
    backend_code = backend.poll()
    if backend_code is not None:
        print(f"Backend failed to start (exit code {backend_code}).")
        print("Tip: check if port 8000 is already in use or if uvicorn cannot bind in this environment.")
        return int(backend_code)

    frontend = _spawn(["npm", "run", "dev"], FRONTEND_DIR)
    procs = [backend, frontend]

    print("Platform started:")
    print("  Backend:  http://127.0.0.1:8000")
    print("  Frontend: http://127.0.0.1:5173")
    print("Press Ctrl+C to stop both.")

    try:
        while True:
            for proc in procs:
                code = proc.poll()
                if code is not None:
                    print(f"Process exited with code {code}. Shutting down others...")
                    for other in procs:
                        if other.poll() is None:
                            other.terminate()
                    for other in procs:
                        if other.poll() is None:
                            other.wait(timeout=5)
                    return int(code)
            time.sleep(0.4)
    except KeyboardInterrupt:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        for proc in procs:
            if proc.poll() is None:
                proc.wait(timeout=5)
        print("\nStopped.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run project stacks from one command.")
    parser.add_argument(
        "target",
        choices=["streamlit", "backend", "frontend", "platform"],
        help="Which stack/component to run.",
    )
    args = parser.parse_args()

    if args.target == "streamlit":
        return _run_blocking([sys.executable, "-m", "streamlit", "run", "app/main.py"], ROOT)
    if args.target == "backend":
        if not _module_available("uvicorn"):
            print("Missing dependency: uvicorn")
            print(f"Install with: {sys.executable} -m pip install -r platform/backend/requirements.txt")
            return 1
        return _run_blocking(_backend_cmd(reload=True), BACKEND_DIR)
    if args.target == "frontend":
        return _run_blocking(["npm", "run", "dev"], FRONTEND_DIR)
    return _run_platform_dual()


if __name__ == "__main__":
    raise SystemExit(main())
