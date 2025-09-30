#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def run_backend():
    env = os.environ.copy()
    # Ensure .env in backend is loaded by the service itself; here just pass through
    cmd = [sys.executable, str(BACKEND_DIR / "async_quart_service.py")]
    return subprocess.Popen(cmd, cwd=str(BACKEND_DIR))


def wait_for_backend(port: int = 9000, timeout: int = 30):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            try:
                s.connect(("127.0.0.1", port))
                return True
            except Exception:
                time.sleep(1)
    return False


def ensure_frontend_built():
    # Install deps if node_modules missing
    if not (FRONTEND_DIR / "node_modules").exists():
        subprocess.check_call(["npm", "install"], cwd=str(FRONTEND_DIR))
    # Build if build folder missing
    if not (FRONTEND_DIR / "build").exists():
        subprocess.check_call(["npm", "run", "build"], cwd=str(FRONTEND_DIR))


def run_frontend():
    # Ensure build exists
    ensure_frontend_built()
    # Use serve -s build -p configured in README (fallback to npm start if serve not found)
    env = os.environ.copy()
    serve_bin = shutil.which("serve")
    if serve_bin:
        cmd = [serve_bin, "-s", "build", "-p", os.environ.get("FRONTEND_PORT", "3000")]
    else:
        cmd = ["npm", "run", "start"]
    return subprocess.Popen(cmd, cwd=str(FRONTEND_DIR))


def main():
    backend = run_backend()
    print("[run_dev] Backend starting...")
    if not wait_for_backend():
        print("[run_dev] Backend not ready within timeout, continuing anyway...")

    print("[run_dev] Starting frontend...")
    frontend = run_frontend()

    try:
        backend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("[run_dev] Shutting down...")
        for p in [frontend, backend]:
            try:
                if p and p.poll() is None:
                    p.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
