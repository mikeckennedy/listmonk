"""Tests for campaign operations through the public API."""

import datetime

import pytest
from factories import campaign_json, page_json

import listmonk
from listmonk import models

pytestmark = pytest.mark.usefixtures('logged_in')


def test_campaigns_returns_all_campaigns(fake_server):
    fake_server.respond('GET', '/api/campaigns', json=page_json([campaign_json(), campaign_json(id=8, name='Promo')]))

    result = listmonk.campaigns()

    assert [c.id for c in result] == [7, 8]
    assert all(isinstance(c, models.Campaign) for c in result)


def test_campaign_by_id_returns_the_campaign(fake_server):
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})

    campaign = listmonk.campaign_by_id(7)

    assert campaign is not None
    assert campaign.subject == 'Our June Update'
    assert campaign.status == 'draft'


def test_campaign_by_id_returns_none_when_missing(fake_server):
    fake_server.respond('GET', '/api/campaigns/123', json={'data': {}})
    assert listmonk.campaign_by_id(123) is None


def test_campaign_preview_returns_the_rendered_html(fake_server):
    fake_server.respond('GET', '/api/campaigns/7/preview', text='<h1>Big news</h1>')

    preview = listmonk.campaign_preview_by_id(7)

    assert preview.preview == '<h1>Big news</h1>'


def test_create_campaign_posts_payload_with_defaults(fake_server):
    fake_server.respond('POST', '/api/campaigns', json={'data': campaign_json(id=9, name='Launch Day')})

    campaign = listmonk.create_campaign('Launch Day', 'We are live!', content_type='markdown', body='# Live now')

    assert campaign.id == 9
    payload = fake_server.last_request.json
    assert payload['name'] == 'Launch Day'
    assert payload['subject'] == 'We are live!'
    assert payload['lists'] == [1]  # the default list
    assert payload['content_type'] == 'markdown'
    assert payload['body'] == '# Live now'
    assert payload['media'] == []


def test_create_campaign_serializes_the_scheduled_send_time(fake_server):
    fake_server.respond('POST', '/api/campaigns', json={'data': campaign_json()})
    send_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)

    listmonk.create_campaign('Scheduled', 'Coming soon', send_at=send_at)

    sent = fake_server.last_request.json['send_at']
    assert isinstance(sent, str)
    assert datetime.datetime.fromisoformat(sent) == send_at


@pytest.mark.parametrize('name, subject', [('', 'Subject'), ('   ', 'Subject'), ('Name', '')])
def test_create_campaign_requires_name_and_subject(fake_server, name, subject):
    with pytest.raises(ValueError):
        listmonk.create_campaign(name, subject)
    assert fake_server.requests == []


def test_delete_campaign_deletes_an_existing_campaign(fake_server):
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})
    fake_server.respond('DELETE', '/api/campaigns/7', json={'data': True})

    assert listmonk.delete_campaign(7) is True

    assert [(r.method, r.path) for r in fake_server.requests] == [
        ('GET', '/api/campaigns/7'),
        ('DELETE', '/api/campaigns/7'),
    ]


def test_delete_campaign_returns_false_when_missing(fake_server):
    fake_server.respond('GET', '/api/campaigns/123', json={'data': {}})

    assert listmonk.delete_campaign(123) is False

    assert [r.method for r in fake_server.requests] == ['GET']


def test_delete_campaign_requires_an_id(fake_server):
    with pytest.raises(ValueError):
        listmonk.delete_campaign(0)


def test_update_campaign_keeps_existing_attachments_by_default(fake_server):
    raw = campaign_json(media=[{'id': 5, 'filename': 'deck.pdf'}], lists=[{'id': 1}, {'id': 2}])
    campaign = models.Campaign(**raw)
    fake_server.respond('PUT', '/api/campaigns/7', json={'data': True})
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})

    updated = listmonk.update_campaign(campaign)

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert put.json['media'] == [5]
    assert sorted(put.json['lists']) == [1, 2]
    assert updated is not None
    assert updated.id == 7


def test_update_campaign_can_clear_attachments(fake_server):
    campaign = models.Campaign(**campaign_json(media=[{'id': 5, 'filename': 'deck.pdf'}]))
    fake_server.respond('PUT', '/api/campaigns/7', json={'data': True})
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})

    listmonk.update_campaign(campaign, media_ids=[])

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert put.json['media'] == []


def test_update_campaign_drops_a_stale_send_time(fake_server):
    campaign = models.Campaign(**campaign_json(send_at='2020-01-01T00:00:00.000000Z', status='scheduled'))
    fake_server.respond('PUT', '/api/campaigns/7', json={'data': True})
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})

    listmonk.update_campaign(campaign)

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert put.json['send_at'] is None


def test_update_campaign_requires_a_saved_campaign(fake_server):
    with pytest.raises(ValueError):
        listmonk.update_campaign(models.Campaign(**campaign_json(id=0)))


def test_test_campaign_posts_the_campaign_body_with_the_recipients(fake_server):
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json(lists=[{'id': 1}, {'id': 2}])})
    fake_server.respond('POST', '/api/campaigns/7/test', json={'data': True})

    assert listmonk.test_campaign(7, ['pat@example.com', 'sam@example.com']) is True

    assert [(r.method, r.path) for r in fake_server.requests] == [
        ('GET', '/api/campaigns/7'),
        ('POST', '/api/campaigns/7/test'),
    ]
    payload = fake_server.last_request.json
    assert payload['subscribers'] == ['pat@example.com', 'sam@example.com']
    assert payload['lists'] == [1, 2]
    assert payload['subject'] == 'Our June Update'
    assert payload['body'] == '# Big news\n\nHello there!'
    assert payload['template_id'] == 1


def test_test_campaign_returns_false_when_the_campaign_is_missing(fake_server):
    fake_server.respond('GET', '/api/campaigns/123', json={'data': {}})

    assert listmonk.test_campaign(123, ['pat@example.com']) is False

    assert [r.method for r in fake_server.requests] == ['GET']


def test_test_campaign_requires_at_least_one_email(fake_server):
    with pytest.raises(ValueError):
        listmonk.test_campaign(7, [])
    assert fake_server.requests == []


def test_test_campaign_requires_an_id(fake_server):
    with pytest.raises(ValueError):
        listmonk.test_campaign(0, ['pat@example.com'])
    assert fake_server.requests == []


def test_set_campaign_status_puts_the_new_status(fake_server):
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})
    fake_server.respond('PUT', '/api/campaigns/7/status', json={'data': campaign_json(status='running')})

    campaign = listmonk.set_campaign_status(7, models.CampaignStatuses.running)

    assert campaign is not None
    assert campaign.status == 'running'
    put = fake_server.last_request
    assert (put.method, put.path) == ('PUT', '/api/campaigns/7/status')
    assert put.json == {'status': 'running'}


def test_set_campaign_status_returns_none_when_the_campaign_is_missing(fake_server):
    fake_server.respond('GET', '/api/campaigns/123', json={'data': {}})

    assert listmonk.set_campaign_status(123, models.CampaignStatuses.running) is None

    assert [r.method for r in fake_server.requests] == ['GET']


def test_set_campaign_status_requires_an_id(fake_server):
    with pytest.raises(ValueError):
        listmonk.set_campaign_status(0, models.CampaignStatuses.running)
    assert fake_server.requests == []


@pytest.mark.parametrize(
    'func, expected_status',
    [
        (listmonk.start_campaign, 'running'),
        (listmonk.pause_campaign, 'paused'),
        (listmonk.cancel_campaign, 'cancelled'),
    ],
)
def test_campaign_status_wrappers_send_their_status(fake_server, func, expected_status):
    fake_server.respond('GET', '/api/campaigns/7', json={'data': campaign_json()})
    fake_server.respond('PUT', '/api/campaigns/7/status', json={'data': campaign_json(status=expected_status)})

    campaign = func(7)

    assert campaign is not None
    assert campaign.status == expected_status
    assert fake_server.last_request.json == {'status': expected_status}
