import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Settings:
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    BASE_API_URL: str = field(default_factory=lambda: os.getenv("BASE_API_URL", "https://api.example.com"))
    RETRY_COUNT: int = field(default_factory=lambda: int(os.getenv("RETRY_COUNT", "2")))
    TIMEOUT: int = field(default_factory=lambda: int(os.getenv("TIMEOUT", "5")))
    PERF_LIMIT_MS: int = field(default_factory=lambda: int(os.getenv("PERF_LIMIT_MS", "300")))
    ANOMALY_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("ANOMALY_THRESHOLD", "1.8")))
    MAX_WORKERS: int = field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "4")))
    API_AUTH_TOKEN: str = field(default_factory=lambda: os.getenv("API_AUTH_TOKEN", ""))
    SSL_EXPIRY_THRESHOLD_DAYS: int = field(default_factory=lambda: int(os.getenv("SSL_EXPIRY_THRESHOLD_DAYS", "7")))
    SSL_ENDPOINTS_RAW: str = field(default_factory=lambda: os.getenv("SSL_ENDPOINTS", ""))
    CONTENT_CHECKS_RAW: str = field(default_factory=lambda: os.getenv("CONTENT_CHECKS", ""))
    DB_PINGS_RAW: str = field(default_factory=lambda: os.getenv("DB_PINGS", ""))
    SLACK_WEBHOOK_URL: str = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL", ""))
    TELEGRAM_BOT_TOKEN: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    TELEGRAM_CHAT_ID: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    def __post_init__(self) -> None:
        self.BASE_API_URL = self.BASE_API_URL.rstrip("/")
        self.ssl_endpoints: List[str] = self._parse_string_list(self.SSL_ENDPOINTS_RAW)
        self.content_checks: List[Dict[str, str]] = self._parse_content_checks(self.CONTENT_CHECKS_RAW)
        self.db_ping_targets: List[Dict[str, Any]] = self._parse_db_targets(self.DB_PINGS_RAW)

    @staticmethod
    def _parse_string_list(raw: str) -> List[str]:
        value = (raw or "").strip()
        if not value:
            return []
        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def _parse_content_checks(raw: str) -> List[Dict[str, str]]:
        value = (raw or "").strip()
        if not value:
            return []
        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return []
        results: List[Dict[str, str]] = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                path = str(item.get("path", "")).strip()
                keyword = str(item.get("keyword", "")).strip()
                if path and keyword:
                    results.append({"path": path, "keyword": keyword})
        return results

    @staticmethod
    def _parse_db_targets(raw: str) -> List[Dict[str, Any]]:
        value = (raw or "").strip()
        if not value:
            return []
        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return []
        results: List[Dict[str, Any]] = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                host = str(item.get("host", "")).strip()
                port_value = item.get("port", 0)
                try:
                    port = int(port_value)
                except (ValueError, TypeError):
                    port = 0
                timeout_value = item.get("timeout", 2.0)
                try:
                    timeout = float(timeout_value)
                except (ValueError, TypeError):
                    timeout = 2.0
                if not host or port <= 0:
                    continue
                name = str(item.get("name", host)).strip() or host
                results.append({
                    "name": name,
                    "host": host,
                    "port": port,
                    "timeout": timeout,
                })
        return results


settings = Settings()
