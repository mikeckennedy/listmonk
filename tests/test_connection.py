"""Tests for connection setup: base URL, login, health checks, and response error contracts."""

import httpx2
import pytest

import listmonk
from listmonk import errors


def test_set_url_base_stores_and_strips_trailing_slash():
    listmonk.set_url_base('https://lm.example.com/')
    assert listmonk.get_base_url() == 'https://lm.example.com'


@pytest.mark.parametrize('bad_url', ['', '   '])
def test_set_url_base_rejects_empty_urls(bad_url):
    with pytest.raises(errors.ValidationError):
        listmonk.set_url_base(bad_url)


def test_set_url_base_requires_http_scheme():
    with pytest.raises(errors.ValidationError):
        listmonk.set_url_base('lm.example.com')


def test_login_accepts_valid_credentials(fake_server):
    fake_server.respond('GET', '/api/health', json={'data': True})
    listmonk.set_url_base('https://lm.example.com')

    assert listmonk.login('admin', 'super-secret') is True

    request = fake_server.last_request
    assert request.path == '/api/health'
    assert isinstance(request.auth, httpx2.BasicAuth)


def test_login_reports_rejected_credentials(fake_server):
    fake_server.respond('GET', '/api/health', status_code=401)
    listmonk.set_url_base('https://lm.example.com')

    assert listmonk.login('admin', 'wrong-password') is False


def test_login_requires_url_base_first():
    with pytest.raises(errors.OperationNotAllowedError):
        listmonk.login('admin', 'super-secret')


@pytest.mark.parametrize('user_name, pw', [('', 'super-secret'), ('admin', '')])
def test_login_rejects_blank_credentials(user_name, pw):
    listmonk.set_url_base('https://lm.example.com')
    with pytest.raises(errors.ValidationError):
        listmonk.login(user_name, pw)


@pytest.mark.parametrize(
    'call',
    [listmonk.lists, listmonk.subscribers, listmonk.campaigns, listmonk.templates],
    ids=['lists', 'subscribers', 'campaigns', 'templates'],
)
def test_api_calls_require_login(fake_server, call):
    listmonk.set_url_base('https://lm.example.com')

    with pytest.raises(errors.OperationNotAllowedError):
        call()

    assert fake_server.requests == []


def test_is_healthy_when_server_is_up(fake_server, logged_in):
    fake_server.respond('GET', '/api/health', json={'data': True})
    assert listmonk.is_healthy() is True


def test_is_healthy_false_on_server_error(fake_server, logged_in):
    fake_server.respond('GET', '/api/health', status_code=500)
    assert listmonk.is_healthy() is False


def test_is_healthy_false_when_never_configured(fake_server):
    assert listmonk.is_healthy() is False
    assert fake_server.requests == []


def test_verify_login_checks_the_health_endpoint(fake_server, logged_in):
    fake_server.respond('GET', '/api/health', json={'data': True})
    assert listmonk.verify_login() is True


def test_empty_response_body_raises_validation_error(fake_server, logged_in):
    fake_server.respond('GET', '/api/lists', status_code=200)
    with pytest.raises(errors.ValidationError, match='Empty response'):
        listmonk.lists()


def test_non_json_response_raises_validation_error(fake_server, logged_in):
    fake_server.respond('GET', '/api/lists', text='<html>proxy error page</html>')
    with pytest.raises(errors.ValidationError, match='Invalid JSON'):
        listmonk.lists()


def test_http_error_status_propagates(fake_server, logged_in):
    fake_server.respond('GET', '/api/lists', status_code=503, json={'message': 'down for maintenance'})
    with pytest.raises(httpx2.HTTPStatusError):
        listmonk.lists()
