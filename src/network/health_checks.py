import datetime
import socket
import ssl
from typing import Tuple


def _parse_host(entry: str) -> Tuple[str, int]:
    value = (entry or "").strip()
    if not value:
        raise ValueError("SSL endpoint entry is empty")
    if value.startswith("https://"):
        value = value[len("https://") :]
    elif value.startswith("http://"):
        value = value[len("http://") :]
    if "/" in value:
        value = value.split("/", 1)[0]
    if ":" in value:
        host, port_part = value.rsplit(":", 1)
        try:
            port = int(port_part)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid port in SSL endpoint '{entry}'") from exc
    else:
        host = value
        port = 443
    host = host.strip()
    if not host:
        raise ValueError(f"Invalid SSL endpoint '{entry}'")
    return host, port


def check_ssl_certificate(entry: str, threshold_days: int) -> Tuple[bool, int, str]:
    host, port = _parse_host(entry)
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as secured:
                cert = secured.getpeercert()
    except Exception as exc:
        return False, 0, f"connection failed: {exc}"

    not_after = cert.get("notAfter")
    if not not_after:
        return False, 0, "certificate missing notAfter field"

    try:
        expiry = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
    except ValueError as exc:
        return False, 0, f"unable to parse expiry: {exc}"

    now = datetime.datetime.utcnow()
    remaining = expiry - now
    days_left = int(remaining.total_seconds() // 86400)
    if remaining.total_seconds() < 0:
        return False, days_left, f"expired {abs(days_left)} day(s) ago"

    if days_left < threshold_days:
        return False, days_left, f"expiring in {days_left} day(s)"

    return True, days_left, f"valid for {days_left} day(s)"


def check_keyword_response(response_text: str, keyword: str) -> Tuple[bool, str]:
    if keyword.lower() in response_text.lower():
        return True, f"keyword '{keyword}' located"
    return False, f"keyword '{keyword}' not found"
