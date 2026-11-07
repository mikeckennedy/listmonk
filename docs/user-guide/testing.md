# Testing your integration

Your app's tests should not send real email, and they should not need a Listmonk server running on the CI machine. The library makes that easy because of how it is built: every request goes through the module-level `httpx2.get`, `httpx2.post`, `httpx2.put`, and `httpx2.delete` functions. Patch those four and the whole client talks to whatever you put behind them.

This is exactly how the library's own suite works. The pattern below is a trimmed version of its `tests/conftest.py`.


# A fake server in forty lines

``` python
import functools
from typing import Any
from urllib.parse import urlsplit

import httpx2
import pytest

from listmonk import impl


class FakeListmonk:
    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], tuple[int, Any]] = {}
        self.requests: list[dict[str, Any]] = []

    def respond(self, method: str, path: str, *, json: Any = None, status_code: int = 200) -> None:
        self.routes[(method.upper(), path)] = (status_code, json)

    def handle(self, method: str, url: str, **kwargs: Any) -> httpx2.Response:
        path = urlsplit(url).path
        self.requests.append({'method': method, 'path': path, 'url': url, **kwargs})
        status_code, body = self.routes[(method, path)]
        request = httpx2.Request(method, url)
        return httpx2.Response(status_code, request=request, json=body)


@pytest.fixture
def fake_listmonk(monkeypatch: pytest.MonkeyPatch) -> FakeListmonk:
    server = FakeListmonk()
    for verb in ('get', 'post', 'put', 'delete'):
        monkeypatch.setattr(httpx2, verb, functools.partial(server.handle, verb.upper()))
    # Skip the login round trip: put the client straight into the logged-in state.
    monkeypatch.setattr(impl, 'url_base', 'https://listmonk.test')
    monkeypatch.setattr(impl, 'username', 'api')
    monkeypatch.setattr(impl, 'password', 'token')
    monkeypatch.setattr(impl, 'has_logged_in', True)
    return server
```

Returning real `httpx2.Response` objects matters. The client calls `raise_for_status()` and `.json()` on them, so a status code of 4xx in `respond()` produces a genuine `httpx2.HTTPStatusError`, and your error-handling code is exercised for real.


# Using it

``` python
def test_signup_creates_a_new_subscriber(fake_listmonk):
    # Lookup finds nobody, then the create succeeds.
    fake_listmonk.respond('GET', '/api/subscribers', json={'data': {'results': [], 'total': 0}})
    fake_listmonk.respond('POST', '/api/subscribers', json={'data': {
        'id': 7, 'email': 'jane@example.com', 'name': 'Jane', 'status': 'enabled',
        'created_at': '2026-01-01T00:00:00.000000Z', 'lists': [], 'attribs': {},
    }})

    subscribe_to_newsletter('jane@example.com', 'Jane', source='test')

    post = next(r for r in fake_listmonk.requests if r['method'] == 'POST')
    assert post['json']['email'] == 'jane@example.com'
    assert post['json']['lists'] == [7]
```

Assert on the recorded request when the interesting part is what your code asked Listmonk to do, and on the return value when the interesting part is how your code reacted. Both are available.


# Shapes the fake has to produce

The client expects Listmonk's real response envelopes, so the fake has to speak them:

- Collection endpoints (`/api/subscribers`, `/api/lists`, `/api/campaigns`) wrap results as `{'data': {'results': [...], 'total': N}}`. [subscribers()](../reference/subscribers.md#listmonk.subscribers) pages until `total` is reached, so set `total` to the number of results you return unless you are testing pagination.
- `/api/templates` is the exception and returns a flat list: `{'data': [...]}`.
- Single-item endpoints return `{'data': {...}}`. Deletes and status endpoints return `{'data': true}`.
- Campaign and template previews return raw HTML, not JSON. `httpx2.Response(200, request=request, text='<h1>Hi</h1>')` does it.
- The direct subscriber endpoint `/api/subscribers/{id}` answers an unknown ID with status 400; the client turns that into `None`.
- Timestamps are ISO strings such as `'2026-01-01T00:00:00.000000Z'`; the models parse them into `datetime` objects.


# What the library's own tests check

If you want to see the full version, the repository's [tests](https://github.com/mikeckennedy/listmonk/tree/main/tests) run every public function against an in-memory fake with canned payloads shaped like real Listmonk responses. They are a good source of realistic JSON when you need a [Campaign](../reference/models.Campaign.md#listmonk.models.Campaign) or [Subscriber](../reference/models.Subscriber.md#listmonk.models.Subscriber) body for your own fixtures.


# Integration tests against a real instance

For an occasional end-to-end check, the repository's `example_client/client.py` exercises every major operation against a live Listmonk, reading its settings from a local JSON file. Run it against a staging instance with a throwaway list rather than production; it creates and deletes subscribers, lists, campaigns, and templates as it goes.
