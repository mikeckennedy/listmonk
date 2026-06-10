"""Tests for subscriber operations through the public API."""

import httpx2
import pytest
from factories import page_json, subscriber_json

import listmonk
from listmonk import models

pytestmark = pytest.mark.usefixtures('logged_in')


def test_subscriber_by_email_returns_the_full_subscriber(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json()]))

    sub = listmonk.subscriber_by_email('pat@example.com')

    assert sub is not None
    assert sub.id == 42
    assert sub.email == 'pat@example.com'
    assert sub.attribs == {'city': 'Portland'}
    assert fake_server.last_request.params['query'] == "subscribers.email='pat@example.com'"


def test_subscriber_by_email_returns_none_for_unknown_email(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([]))
    assert listmonk.subscriber_by_email('nobody@example.com') is None


def test_subscriber_by_email_handles_plus_addresses(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json(email='pat+news@example.com')]))

    sub = listmonk.subscriber_by_email('pat+news@example.com')

    assert sub is not None
    # The + must travel as %2b in the raw URL so the server doesn't read it as a space.
    assert '%2b' in fake_server.last_request.url
    assert fake_server.last_request.params['query'] == "subscribers.email='pat+news@example.com'"


def test_subscriber_by_id_queries_by_id(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json()]))

    sub = listmonk.subscriber_by_id(42)

    assert sub is not None
    assert sub.id == 42
    assert fake_server.last_request.params['query'] == 'subscribers.id=42'


def test_subscriber_by_id_returns_none_for_unknown_id(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([]))
    assert listmonk.subscriber_by_id(999_999) is None


def test_subscriber_by_uuid_queries_by_uuid(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json()]))

    sub = listmonk.subscriber_by_uuid('c37786af-e6ab-4260-9b49-740a8cd6a7ed')

    assert sub is not None
    assert sub.uuid == 'c37786af-e6ab-4260-9b49-740a8cd6a7ed'
    assert fake_server.last_request.params['query'] == "subscribers.uuid='c37786af-e6ab-4260-9b49-740a8cd6a7ed'"


def test_subscribers_fetches_all_pages(fake_server):
    page_one = [subscriber_json(id=1, email='a@example.com'), subscriber_json(id=2, email='b@example.com')]
    page_two = [subscriber_json(id=3, email='c@example.com')]
    fake_server.respond('GET', '/api/subscribers', json=page_json(page_one, total=502))
    fake_server.respond('GET', '/api/subscribers', json=page_json(page_two, total=502, page=2))

    subs = listmonk.subscribers()

    assert [s.id for s in subs] == [1, 2, 3]
    assert [r.params['page'] for r in fake_server.requests] == ['1', '2']


def test_subscribers_passes_search_criteria(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([]))

    listmonk.subscribers(query_text="subscribers.attribs->>'city' = 'Portland'", list_id=4)

    params = fake_server.last_request.params
    assert params['list_id'] == '4'
    assert params['query'] == "subscribers.attribs->>'city' = 'Portland'"


def test_create_subscriber_normalizes_and_posts(fake_server):
    fake_server.respond('POST', '/api/subscribers', json={'data': subscriber_json(id=77, email='new@example.com')})

    sub = listmonk.create_subscriber(
        '  NEW@Example.COM ', name='New Person', list_ids={1, 4}, pre_confirm=True, attribs={'source': 'webinar'}
    )

    assert sub.id == 77
    payload = fake_server.last_request.json
    assert payload['email'] == 'new@example.com'
    assert payload['name'] == 'New Person'
    assert payload['status'] == 'enabled'
    assert sorted(payload['lists']) == [1, 4]
    assert payload['preconfirm_subscriptions'] is True
    assert payload['attribs'] == {'source': 'webinar'}


@pytest.mark.parametrize('email', ['', '   ', None])
def test_create_subscriber_requires_an_email(fake_server, email):
    with pytest.raises(ValueError):
        listmonk.create_subscriber(email)
    assert fake_server.requests == []


def test_create_subscriber_surfaces_server_rejection(fake_server):
    fake_server.respond('POST', '/api/subscribers', status_code=409, json={'message': 'E-mail already exists.'})
    with pytest.raises(httpx2.HTTPStatusError):
        listmonk.create_subscriber('pat@example.com')


def test_delete_subscriber_by_email_looks_up_then_deletes(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json()]))
    fake_server.respond('DELETE', '/api/subscribers/42', json={'data': True})

    assert listmonk.delete_subscriber('pat@example.com') is True

    assert [(r.method, r.path) for r in fake_server.requests] == [
        ('GET', '/api/subscribers'),
        ('DELETE', '/api/subscribers/42'),
    ]


def test_delete_subscriber_returns_false_for_unknown_email(fake_server):
    fake_server.respond('GET', '/api/subscribers', json=page_json([]))

    assert listmonk.delete_subscriber('nobody@example.com') is False

    assert [r.method for r in fake_server.requests] == ['GET']


def test_delete_subscriber_by_id_skips_the_lookup(fake_server):
    fake_server.respond('DELETE', '/api/subscribers/42', json={'data': True})

    assert listmonk.delete_subscriber(overriding_subscriber_id=42) is True

    assert [r.method for r in fake_server.requests] == ['DELETE']


def test_delete_subscriber_requires_a_target(fake_server):
    with pytest.raises(ValueError):
        listmonk.delete_subscriber()


def test_update_subscriber_merges_list_membership(fake_server):
    sub = models.Subscriber(**subscriber_json(lists=[{'id': 1}, {'id': 2}]))
    fake_server.respond('PUT', '/api/subscribers/42', json={'data': True})
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json()]))

    updated = listmonk.update_subscriber(sub, add_to_lists={3}, remove_from_lists={2})

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert sorted(put.json['lists']) == [1, 3]
    assert put.json['preconfirm_subscriptions'] is True
    assert updated is not None
    assert updated.id == 42


def test_update_subscriber_requires_a_saved_subscriber(fake_server):
    unsaved = models.Subscriber(**subscriber_json(id=0))
    with pytest.raises(ValueError):
        listmonk.update_subscriber(unsaved)


@pytest.mark.parametrize(
    'change_status, expected',
    [
        (listmonk.enable_subscriber, 'enabled'),
        (listmonk.disable_subscriber, 'disabled'),
        (listmonk.block_subscriber, 'blocklisted'),
    ],
    ids=['enable', 'disable', 'block'],
)
def test_status_helpers_send_the_right_status(fake_server, change_status, expected):
    sub = models.Subscriber(**subscriber_json())
    fake_server.respond('PUT', '/api/subscribers/42', json={'data': True})
    fake_server.respond('GET', '/api/subscribers', json=page_json([subscriber_json(status=expected)]))

    updated = change_status(sub)

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert put.json['status'] == expected
    assert updated is not None
    assert updated.status == expected


def test_add_subscribers_to_lists_bulk_adds(fake_server):
    fake_server.respond('PUT', '/api/subscribers/lists', json={'data': True})

    assert listmonk.add_subscribers_to_lists([42, 42, 7], [1, 2], status='unconfirmed') is True

    payload = fake_server.last_request.json
    assert sorted(payload['ids']) == [7, 42]
    assert sorted(payload['target_list_ids']) == [1, 2]
    assert payload['action'] == 'add'
    assert payload['status'] == 'unconfirmed'


@pytest.mark.parametrize('subscriber_ids, list_ids', [([], [1]), ([42], []), ([0], [1]), ([42], [0])])
def test_add_subscribers_to_lists_rejects_empty_input(fake_server, subscriber_ids, list_ids):
    assert listmonk.add_subscribers_to_lists(subscriber_ids, list_ids) is False
    assert fake_server.requests == []


def test_add_subscribers_to_lists_reports_server_error_as_false(fake_server):
    fake_server.respond('PUT', '/api/subscribers/lists', status_code=500)
    assert listmonk.add_subscribers_to_lists([42], [1]) is False


def test_confirm_optin_submits_the_optin_form(fake_server):
    fake_server.respond('POST', '/subscription/optin/sub-uuid-1', text='<html>Confirmed</html>')

    assert listmonk.confirm_optin('sub-uuid-1', 'list-uuid-9') is True

    assert fake_server.last_request.data == {'l': 'list-uuid-9', 'confirm': 'true'}


def test_confirm_optin_reports_failure_as_false(fake_server):
    fake_server.respond('POST', '/subscription/optin/sub-uuid-1', status_code=404, text='not found')
    assert listmonk.confirm_optin('sub-uuid-1', 'list-uuid-9') is False


@pytest.mark.parametrize('sub_uuid, list_uuid', [('', 'list-uuid-9'), ('sub-uuid-1', '')])
def test_confirm_optin_requires_both_uuids(fake_server, sub_uuid, list_uuid):
    with pytest.raises(ValueError):
        listmonk.confirm_optin(sub_uuid, list_uuid)
    assert fake_server.requests == []
