"""Shared test infrastructure for the listmonk client test suite.

The library talks to a Listmonk server through module-level httpx2 calls. These
fixtures swap those calls for an in-memory fake server, so every test exercises
the real public API end to end (URL building, payload construction, response
parsing, and error handling) without any network traffic.
"""

import dataclasses
import functools
from typing import Any, Optional
from urllib.parse import parse_qsl, urlsplit

import httpx2
import pytest

from listmonk import impl

BASE_URL = 'https://listmonk.unit.test'


@dataclasses.dataclass
class RecordedRequest:
    """One request captured by the fake server, with the parts tests assert on."""

    method: str
    url: str
    path: str
    params: dict[str, str]
    json: Optional[Any]
    data: Optional[Any]
    files: Optional[Any]
    headers: Optional[dict[str, str]]
    auth: Optional[Any]


class FakeListmonkServer:
    """An in-memory stand-in for a Listmonk instance.

    Register canned responses with respond(); registering the same method and path
    again queues responses to be returned in order (the last one repeats). Every
    request the library sends is captured in `requests`. An unregistered request
    raises AssertionError, though library functions that swallow all exceptions
    (e.g. is_healthy) surface that as a False return value instead.
    """

    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], list[tuple[int, Optional[Any], Optional[str]]]] = {}
        self.requests: list[RecordedRequest] = []

    def respond(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        text: Optional[str] = None,
        status_code: int = 200,
    ) -> None:
        self._routes.setdefault((method.upper(), path), []).append((status_code, json, text))

    @property
    def last_request(self) -> RecordedRequest:
        return self.requests[-1]

    def handle(self, method: str, url: str, **kwargs: Any) -> httpx2.Response:
        parts = urlsplit(url)
        self.requests.append(
            RecordedRequest(
                method=method,
                url=url,
                path=parts.path,
                params=dict(parse_qsl(parts.query)),
                json=kwargs.get('json'),
                data=kwargs.get('data'),
                files=kwargs.get('files'),
                headers=kwargs.get('headers'),
                auth=kwargs.get('auth'),
            )
        )

        queue = self._routes.get((method, parts.path))
        if not queue:
            registered = sorted(self._routes) or 'nothing'
            raise AssertionError(f'Unexpected request: {method} {parts.path} (registered: {registered})')

        status_code, json_body, text = queue.pop(0) if len(queue) > 1 else queue[0]
        response_kwargs: dict[str, Any] = {}
        if json_body is not None:
            response_kwargs['json'] = json_body
        elif text is not None:
            response_kwargs['text'] = text

        return httpx2.Response(status_code, request=httpx2.Request(method, url), **response_kwargs)


@pytest.fixture(autouse=True)
def fake_server(monkeypatch: pytest.MonkeyPatch) -> FakeListmonkServer:
    """Route all httpx2 traffic to a fresh fake server, so no test can hit the network."""
    server = FakeListmonkServer()
    for verb in ('get', 'post', 'put', 'delete'):
        monkeypatch.setattr(httpx2, verb, functools.partial(server.handle, verb.upper()))
    return server


@pytest.fixture(autouse=True)
def clean_client_state():
    """Reset the library's module-level connection state around every test."""
    impl.url_base = None
    impl.username = None
    impl.password = None
    impl.has_logged_in = False
    yield
    impl.url_base = None
    impl.username = None
    impl.password = None
    impl.has_logged_in = False


@pytest.fixture
def logged_in(clean_client_state):
    """Put the client in the state produced by set_url_base() plus a successful login()."""
    impl.url_base = BASE_URL
    impl.username = 'admin'
    impl.password = 'super-secret'
    impl.has_logged_in = True
