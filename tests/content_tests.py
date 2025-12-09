import time

from core.registry import test
from core.assertions import check
from core.settings import settings
from network.health_checks import check_keyword_response
from network.http_client import client
from report.reporter import REPORTER, TestResult


@test(name="API Content Keywords", tags=["content", "api"])
def test_content_keywords() -> None:
    start = time.time()
    checks = settings.content_checks
    if not checks:
        REPORTER.add(
            TestResult(
                name="API Content Keywords",
                status="SKIPPED",
                duration_ms=(time.time() - start) * 1000,
                tags=["content", "api"],
                details="No content checks configured",
            )
        )
        return

    failures = []
    details = []
    for item in checks:
        path = item["path"]
        keyword = item["keyword"]
        response = client.get(path)
        if response.status_code != 200:
            failures.append(f"{path} returned {response.status_code}")
            details.append(f"{path}: unexpected status {response.status_code}")
            continue
        body_text = getattr(response, "text", "")
        if not body_text and hasattr(response, "json"):
            try:
                body_text = str(response.json())
            except Exception:  # pragma: no cover - defensive
                body_text = ""
        ok, message = check_keyword_response(body_text, keyword)
        details.append(f"{path}: {message}")
        if not ok:
            failures.append(f"{path} missing keyword '{keyword}'")

    check(not failures, "Content check issues: " + "; ".join(failures))
    REPORTER.add(
        TestResult(
            name="API Content Keywords",
            status="PASSED",
            duration_ms=(time.time() - start) * 1000,
            tags=["content", "api"],
            details="; ".join(details),
        )
    )
