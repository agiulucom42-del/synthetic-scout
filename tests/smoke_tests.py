import time

from core.registry import test
from core.assertions import check, TestAssertionError
from core.settings import settings
from network.http_client import client
from report.reporter import REPORTER, TestResult


@test(name="API Healthcheck", tags=["smoke", "api"])
def test_health():
    start = time.time()
    resp = client.get("/health")
    elapsed_ms = (time.time() - start) * 1000

    check(resp.status_code == 200, f"Status 200 bekleniyordu, geldi: {resp.status_code}")
    try:
        data = resp.json()
    except Exception as e:
        raise TestAssertionError(f"JSON parse hatası: {e}")

    check(data.get("status") == "ok", f"JSON['status'] 'ok' olmalı, geldi: {data.get('status')}")

    REPORTER.add(
        TestResult(
            name="API Healthcheck",
            status="PASSED",
            duration_ms=elapsed_ms,
            tags=["smoke", "api"],
        )
    )


@test(name="API Health Performance", tags=["perf", "api"])
def perf_health():
    start = time.time()
    resp = client.get("/health")
    elapsed_ms = (time.time() - start) * 1000

    check(resp.status_code == 200, f"Status 200 bekleniyordu, geldi: {resp.status_code}")
    check(
        elapsed_ms < settings.PERF_LIMIT_MS,
        f"Health endpoint {settings.PERF_LIMIT_MS} ms altında olmalı, ölçülen: {elapsed_ms:.2f} ms",
    )

    REPORTER.add(
        TestResult(
            name="API Health Performance",
            status="PASSED",
            duration_ms=elapsed_ms,
            tags=["perf", "api"],
        )
    )
