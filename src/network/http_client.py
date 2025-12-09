import json
import logging
import os
from typing import Dict, Optional, Tuple

import requests

from core.settings import settings

log = logging.getLogger("it_tester.http")


class FakeResponse:
    """Minimal response object to emulate requests.Response."""

    def __init__(self, status_code: int, payload: Dict[str, object]) -> None:
        self.status_code = status_code
        self._payload = payload
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}

    def json(self) -> Dict[str, object]:
        return self._payload

    @property
    def text(self) -> str:
        return json.dumps(self._payload)


class FakeHttpClient:
    """In-memory HTTP client to make tests deterministic."""

    _ROUTES: Dict[Tuple[str, str], Tuple[int, Dict[str, object]]] = {
        ("GET", "/health"): (200, {"status": "ok"}),
        (
            "POST",
            "/auth/login",
        ): (
            200,
            {
                "token": "mock-token",
                "user": {
                    "username": "test_user",
                    "roles": ["tester"],
                },
            },
        ),
    }

    def __init__(self) -> None:
        self.base_url = "mock://it-tester"
        self.timeout = 0
        self.retries = 0

    def request(self, method: str, path: str, **kwargs) -> FakeResponse:
        method = method.upper()
        if not path.startswith("/"):
            path = f"/{path}"
        route = self._ROUTES.get((method, path))
        if not route:
            raise RuntimeError(f"No fake response configured for {method} {path}")
        status_code, payload = route
        return FakeResponse(status_code, payload)

    def get(self, path: str, **kwargs) -> FakeResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> FakeResponse:
        return self.request("POST", path, **kwargs)


class HttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: int,
        retries: int,
        api_token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        if api_token:
            self.session.headers.update({"Authorization": f"Bearer {api_token}"})

    def _full_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._full_url(path)
        last_exc: Optional[Exception] = None

        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )
                if response.status_code in (502, 503, 504) and attempt < self.retries:
                    log.warning(
                        "Received %s for %s; retrying attempt %s",
                        response.status_code,
                        url,
                        attempt + 1,
                    )
                    self._backoff(attempt)
                    continue
                return response
            except Exception as exc:
                last_exc = exc
                if attempt < self.retries:
                    log.warning(
                        "Request to %s failed: %s; retrying attempt %s",
                        url,
                        exc,
                        attempt + 1,
                    )
                    self._backoff(attempt)
                    continue
                log.error("Request to %s failed permanently: %s", url, exc)
                raise last_exc
        raise last_exc if last_exc else RuntimeError("HttpClient request failed unexpectedly")

    def _backoff(self, attempt: int) -> None:
        import time as _time

        _time.sleep(0.2 * (attempt + 1))

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)


def _should_use_fake_client() -> bool:
    override = os.getenv("IT_TESTER_USE_FAKE_API")
    if override is not None:
        return override.lower() in {"1", "true", "yes"}

    base = settings.BASE_API_URL.strip()
    if not base:
        return True
    if not base.startswith("http://") and not base.startswith("https://"):
        return True
    default_base = "https://api.example.com"
    return base.rstrip("/") == default_base


def _create_client() -> FakeHttpClient | HttpClient:
    if _should_use_fake_client():
        log.info("Using FakeHttpClient for tests")
        return FakeHttpClient()
    return HttpClient(
        base_url=settings.BASE_API_URL,
        timeout=settings.TIMEOUT,
        retries=settings.RETRY_COUNT,
        api_token=settings.API_AUTH_TOKEN or None,
    )


client = _create_client()
