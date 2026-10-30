"""Core port helpers."""

from __future__ import annotations

import socket
import subprocess
import time


def is_free(port: int, host: str = "127.0.0.1") -> bool:
    """True if nothing is listening on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find(preferred: int, tries: int = 100, host: str = "127.0.0.1") -> int:
    """Return `preferred` if free, otherwise the next free port above it.

    Raises OSError if nothing is free within `tries` steps.
    """
    if not 1 <= preferred <= 65535:
        raise ValueError(f"port out of range: {preferred}")
    for offset in range(tries):
        candidate = preferred + offset
        if candidate > 65535:
            break
        if is_free(candidate, host):
            return candidate
    raise OSError(f"no free port in [{preferred}, {preferred + tries})")


def wait_open(port: int, timeout: float = 10.0, host: str = "127.0.0.1",
              interval: float = 0.1) -> float:
    """Block until something accepts on host:port. Returns seconds waited.

    Raises TimeoutError if it never opens. Useful right after spawning a
    server process so the next step does not race the listener.
    """
    start = time.monotonic()
    deadline = start + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(interval)
            if s.connect_ex((host, port)) == 0:
                return time.monotonic() - start
        time.sleep(interval)
    raise TimeoutError(f"{host}:{port} did not open within {timeout}s")


def who(port: int) -> str | None:
    """Best-effort: which process holds `port`. None if unknown.

    Shells out to lsof (macOS/Linux). Returns None rather than raising when
    lsof is missing or the lookup fails -- this is a convenience, not a
    dependency.
    """
    try:
        out = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-F", "cp"],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None

    pid = name = ""
    for line in out.splitlines():
        if line.startswith("p"):
            pid = line[1:]
        elif line.startswith("c"):
            name = line[1:]
            break
    if not name:
        return None
    return f"{name} (pid {pid})" if pid else name
