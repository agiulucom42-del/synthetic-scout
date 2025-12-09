import socket
from typing import Dict, Tuple


def tcp_ping(target: Dict[str, object]) -> Tuple[bool, str]:
    host = str(target.get("host", "")).strip()
    port = int(target.get("port", 0))
    timeout = float(target.get("timeout", 2.0))
    if not host or port <= 0:
        return False, "invalid host or port"
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "connection successful"
    except Exception as exc:
        return False, f"connection failed: {exc}"
