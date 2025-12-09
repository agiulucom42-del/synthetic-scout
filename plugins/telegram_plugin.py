import logging
from typing import Any, Dict

import requests

from core.settings import settings
from plugins.base import Plugin
from report.reporter import TestResult

log = logging.getLogger("it_tester.telegram_plugin")


class TelegramPlugin(Plugin):
    def __init__(self) -> None:
        self.bot_token = settings.TELEGRAM_BOT_TOKEN.strip()
        self.chat_id = settings.TELEGRAM_CHAT_ID.strip()
        self.enabled = bool(self.bot_token and self.chat_id)

    def _send(self, text: str) -> None:
        if not self.enabled:
            return
        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(api_url, json=payload, timeout=5)
        except Exception as exc:
            log.warning("Telegram notification failed: %s", exc)

    def on_start(self, context: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        text = (
            "*IT-Tester started*\n"
            f"Environment: `{context.get('env')}`\nTests: `{context.get('test_count')}`"
        )
        self._send(text)

    def on_test_result(self, result: TestResult) -> None:
        if not self.enabled:
            return
        if result.status not in {"FAILED", "ERROR"}:
            return
        text = (
            f"*Alert* — `{result.name}`\n"
            f"Status: `{result.status}`\n"
            f"Details: {result.details or 'n/a'}"
        )
        self._send(text)

    def on_finish(self, summary: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        text = (
            "*IT-Tester finished*\n"
            f"Total: `{summary.get('total')}`\n"
            f"Passed: `{summary.get('passed')}`\nFailed: `{summary.get('failed')}`\n"
            f"Errors: `{summary.get('error')}`\nSkipped: `{summary.get('skipped')}`"
        )
        self._send(text)


def get_plugin() -> Plugin:
    return TelegramPlugin()
