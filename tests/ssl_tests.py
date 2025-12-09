import time

from core.registry import test
from core.assertions import check
from core.settings import settings
from network.health_checks import check_ssl_certificate
from report.reporter import REPORTER, TestResult


@test(name="SSL Certificate Health", tags=["ssl", "monitoring"])
def test_ssl_certificates() -> None:
    start = time.time()
    endpoints = settings.ssl_endpoints
    if not endpoints:
        REPORTER.add(
            TestResult(
                name="SSL Certificate Health",
                status="SKIPPED",
                duration_ms=(time.time() - start) * 1000,
                tags=["ssl", "monitoring"],
                details="No SSL endpoints configured",
            )
        )
        return

    threshold = max(settings.SSL_EXPIRY_THRESHOLD_DAYS, 0)
    failures = []
    details = []
    for entry in endpoints:
        ok, days_left, message = check_ssl_certificate(entry, threshold)
        details.append(f"{entry}: {message}")
        if not ok:
            failures.append(f"{entry} ({message})")

    check(not failures, "SSL issues detected: " + "; ".join(failures))
    REPORTER.add(
        TestResult(
            name="SSL Certificate Health",
            status="PASSED",
            duration_ms=(time.time() - start) * 1000,
            tags=["ssl", "monitoring"],
            details="; ".join(details),
        )
    )
