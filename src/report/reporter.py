import json
import logging
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.settings import settings

log = logging.getLogger("it_tester.report")


@dataclass
class TestResult:
    name: str
    status: str
    duration_ms: Optional[float] = None
    details: str = ""
    tags: List[str] = field(default_factory=list)


class Reporter:
    def __init__(self) -> None:
        Path("reports").mkdir(exist_ok=True)
        self.results: List[TestResult] = []
        self.started_at: float = time.time()

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    def anomaly_count(self) -> int:
        durations = [result.duration_ms for result in self.results if result.duration_ms is not None]
        if len(durations) < 3:
            return 0
        avg = sum(durations) / len(durations)
        variance = sum((duration - avg) ** 2 for duration in durations) / len(durations)
        std_dev = math.sqrt(variance)
        if std_dev == 0:
            return 0
        anomalies = [duration for duration in durations if abs(duration - avg) > settings.ANOMALY_THRESHOLD * std_dev]
        return len(anomalies)

    def summary_dict(self) -> Dict[str, Any]:
        total_time_ms = (time.time() - self.started_at) * 1000
        passed = [result for result in self.results if result.status == "PASSED"]
        failed = [result for result in self.results if result.status == "FAILED"]
        errors = [result for result in self.results if result.status == "ERROR"]
        skipped = [result for result in self.results if result.status == "SKIPPED"]
        return {
            "env": settings.ENV,
            "base_api_url": settings.BASE_API_URL,
            "total": len(self.results),
            "passed": len(passed),
            "failed": len(failed),
            "error": len(errors),
            "skipped": len(skipped),
            "anomaly_count": self.anomaly_count(),
            "total_duration_ms": total_time_ms,
            "results": [
                {
                    "name": result.name,
                    "status": result.status,
                    "duration_ms": result.duration_ms,
                    "tags": result.tags,
                    "details": result.details,
                }
                for result in self.results
            ],
        }

    def save_json(self) -> Path:
        output = Path("reports/summary.json")
        output.write_text(json.dumps(self.summary_dict(), indent=2), encoding="utf-8")
        return output

    def save_junit(self) -> Path:
        total = len(self.results)
        failures = len([result for result in self.results if result.status == "FAILED"])
        errors = len([result for result in self.results if result.status == "ERROR"])
        skipped = len([result for result in self.results if result.status == "SKIPPED"])
        total_time_s = time.time() - self.started_at

        lines: List[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuite name="it-tester" tests="{total}" failures="{failures}" errors="{errors}" skipped="{skipped}" time="{total_time_s:.3f}">',
        ]

        for result in self.results:
            duration_s = (result.duration_ms or 0.0) / 1000.0
            lines.append(f'  <testcase classname="it_tester" name="{result.name}" time="{duration_s:.3f}">')
            if result.status == "FAILED":
                lines.append(f'    <failure message="FAILED"><![CDATA[{result.details}]]></failure>')
            elif result.status == "ERROR":
                lines.append(f'    <error message="ERROR"><![CDATA[{result.details}]]></error>')
            elif result.status == "SKIPPED":
                lines.append(f'    <skipped message="SKIPPED"><![CDATA[{result.details}]]></skipped>')
            lines.append("  </testcase>")

        lines.append("</testsuite>")
        xml_content = "\n".join(lines)
        output = Path("reports/junit.xml")
        output.write_text(xml_content, encoding="utf-8")
        return output

    def save_html(self) -> Path:
        from report import html_formatter

        summary = self.summary_dict()
        html_output = html_formatter.render_html(summary, self.results)
        output = Path("reports/report.html")
        output.write_text(html_output, encoding="utf-8")
        return output


REPORTER = Reporter()
