import logging
from typing import Any, Dict

import requests

from core.settings import settings
from plugins.base import Plugin
from report.reporter import TestResult

log = logging.getLogger("it_tester.slack_plugin")


class SlackPlugin(Plugin):
    def __init__(self) -> None:
        self.webhook_url = settings.SLACK_WEBHOOK_URL.strip()
        self.enabled = bool(self.webhook_url)

    def _post(self, payload: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as exc:
            log.warning("Slack notification failed: %s", exc)

    def on_start(self, context: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        text = f"IT-Tester started for ENV={context.get('env')} (tests={context.get('test_count')})"
        self._post({"text": text})

    def on_test_result(self, result: TestResult) -> None:
        if not self.enabled:
            return
        if result.status not in {"FAILED", "ERROR"}:
            return
        text = f"Alert: {result.name} -> {result.status}\n{result.details}".strip()
        self._post({"text": text})

    def on_finish(self, summary: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        text = (
            "IT-Tester finished: total={total}, passed={passed}, failed={failed}, error={error}, skipped={skipped}".format(
                total=summary.get("total"),
                passed=summary.get("passed"),
                failed=summary.get("failed"),
                error=summary.get("error"),
                skipped=summary.get("skipped"),
            )
        )
        self._post({"text": text})


def get_plugin() -> Plugin:
    return SlackPlugin()
