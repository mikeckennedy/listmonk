"""Tests for mailing list operations through the public API."""

import pytest
from factories import mailing_list_json, page_json

import listmonk
from listmonk import models

pytestmark = pytest.mark.usefixtures('logged_in')


def test_lists_returns_all_mailing_lists(fake_server):
    canned = [mailing_list_json(), mailing_list_json(id=2, name='Friends of the Show')]
    fake_server.respond('GET', '/api/lists', json=page_json(canned))

    result = listmonk.lists()

    assert [lst.id for lst in result] == [1, 2]
    assert all(isinstance(lst, models.MailingList) for lst in result)
    assert result[1].name == 'Friends of the Show'


def test_lists_handles_an_empty_server(fake_server):
    fake_server.respond('GET', '/api/lists', json=page_json([]))
    assert listmonk.lists() == []


def test_list_by_id_returns_the_list(fake_server):
    fake_server.respond('GET', '/api/lists/1', json={'data': mailing_list_json()})

    lst = listmonk.list_by_id(1)

    assert lst.id == 1
    assert lst.name == 'Main Newsletter'
    assert lst.optin == 'single'


def test_list_by_id_picks_the_requested_list_from_results(fake_server):
    # Some listmonk versions return several lists here; the client must pick the right one.
    # See https://github.com/knadh/listmonk/issues/2117
    payload = {'data': {'results': [mailing_list_json(), mailing_list_json(id=7, name='Special')]}}
    fake_server.respond('GET', '/api/lists/7', json=payload)

    lst = listmonk.list_by_id(7)

    assert lst.id == 7
    assert lst.name == 'Special'


def test_list_by_id_raises_when_the_list_is_missing(fake_server):
    fake_server.respond('GET', '/api/lists/99', json={'data': {'results': [mailing_list_json()]}})
    with pytest.raises(Exception, match='99 not found'):
        listmonk.list_by_id(99)


def test_create_list_posts_payload_and_returns_the_new_list(fake_server):
    fake_server.respond('POST', '/api/lists', json={'data': mailing_list_json(id=9, name='Course Announcements')})

    created = listmonk.create_list(
        '  Course Announcements  ', optin='double', tags=['courses'], description='Course news.'
    )

    assert created.id == 9
    payload = fake_server.last_request.json
    assert payload['name'] == 'Course Announcements'
    assert payload['type'] == 'public'
    assert payload['optin'] == 'double'
    assert payload['tags'] == ['courses']
    assert payload['description'] == 'Course news.'


@pytest.mark.parametrize(
    'kwargs',
    [
        {'list_name': '   '},
        {'list_name': 'Ok', 'list_type': 'secret'},
        {'list_name': 'Ok', 'optin': 'triple'},
    ],
    ids=['blank-name', 'bad-type', 'bad-optin'],
)
def test_create_list_rejects_bad_arguments(fake_server, kwargs):
    with pytest.raises(ValueError):
        listmonk.create_list(**kwargs)
    assert fake_server.requests == []


def test_update_list_sends_only_the_provided_fields(fake_server):
    fake_server.respond('PUT', '/api/lists/3', json={'data': mailing_list_json(id=3, name='Renamed')})

    updated = listmonk.update_list(3, list_name='Renamed')

    assert updated.name == 'Renamed'
    assert fake_server.last_request.json == {'name': 'Renamed'}


@pytest.mark.parametrize(
    'kwargs',
    [
        {'list_id': 0},
        {'list_id': 3, 'list_type': 'secret'},
        {'list_id': 3, 'status': 'paused'},
        {'list_id': 3, 'optin': 'triple'},
    ],
    ids=['no-id', 'bad-type', 'bad-status', 'bad-optin'],
)
def test_update_list_rejects_bad_arguments(fake_server, kwargs):
    with pytest.raises(ValueError):
        listmonk.update_list(**kwargs)
    assert fake_server.requests == []


def test_delete_list_checks_existence_then_deletes(fake_server):
    fake_server.respond('GET', '/api/lists/3', json={'data': mailing_list_json(id=3)})
    fake_server.respond('DELETE', '/api/lists/3', json={'data': True})

    assert listmonk.delete_list(3) is True

    assert [(r.method, r.path) for r in fake_server.requests] == [('GET', '/api/lists/3'), ('DELETE', '/api/lists/3')]


def test_delete_list_requires_an_id(fake_server):
    with pytest.raises(ValueError):
        listmonk.delete_list(0)
