import time

from core.registry import test
from core.assertions import check
from core.settings import settings
from network.db_client import tcp_ping
from report.reporter import REPORTER, TestResult


@test(name="Database Connectivity", tags=["db", "infrastructure"])
def test_database_connectivity() -> None:
    start = time.time()
    targets = settings.db_ping_targets
    if not targets:
        REPORTER.add(
            TestResult(
                name="Database Connectivity",
                status="SKIPPED",
                duration_ms=(time.time() - start) * 1000,
                tags=["db", "infrastructure"],
                details="No database targets configured",
            )
        )
        return

    failures = []
    details = []
    for target in targets:
        ok, message = tcp_ping(target)
        details.append(f"{target['name']}: {message}")
        if not ok:
            failures.append(f"{target['name']} ({message})")

    check(not failures, "Database connectivity issues: " + "; ".join(failures))
    REPORTER.add(
        TestResult(
            name="Database Connectivity",
            status="PASSED",
            duration_ms=(time.time() - start) * 1000,
            tags=["db", "infrastructure"],
            details="; ".join(details),
        )
    )
