import logging
from typing import Dict, Any

from report.reporter import TestResult
from plugins.base import Plugin

log = logging.getLogger("it_tester.console_plugin")


class ConsolePlugin(Plugin):
    def on_start(self, context: Dict[str, Any]) -> None:
        log.info(
            "ConsolePlugin: Tests starting -> ENV=%s BASE_API_URL=%s COUNT=%s",
            context.get("env"),
            context.get("base_api_url"),
            context.get("test_count"),
        )

    def on_test_result(self, result: TestResult) -> None:
        log.info("ConsolePlugin: [%s] %s (%.2f ms)",
                 result.status, result.name, result.duration_ms or 0.0)

    def on_finish(self, summary: Dict[str, Any]) -> None:
        log.info(
            "ConsolePlugin: Finished -> total=%s passed=%s failed=%s error=%s skipped=%s anomaly=%s",
            summary.get("total"),
            summary.get("passed"),
            summary.get("failed"),
            summary.get("error"),
            summary.get("skipped"),
            summary.get("anomaly_count"),
        )


def get_plugin() -> Plugin:
    return ConsolePlugin()
