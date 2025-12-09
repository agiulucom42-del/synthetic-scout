import time

from core.registry import test
from core.assertions import check, TestAssertionError
from network.http_client import client
from report.reporter import REPORTER, TestResult


@test(name="API Auth Login", tags=["auth", "api"])
def test_auth_login() -> None:
    start = time.time()
    payload = {"username": "test_user", "password": "test_pass"}
    response = client.post("/auth/login", json=payload)
    elapsed_ms = (time.time() - start) * 1000

    check(response.status_code == 200, f"Expected status 200, got {response.status_code}")
    try:
        data = response.json()
    except Exception as exc:  # noqa: BLE001 - test assertions
        raise TestAssertionError(f"Failed to decode JSON response: {exc}") from exc

    check("token" in data, f"Response is missing token field. Body: {data}")

    REPORTER.add(
        TestResult(
            name="API Auth Login",
            status="PASSED",
            duration_ms=elapsed_ms,
            tags=["auth", "api"],
        )
    )
