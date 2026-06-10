"""Tests for the serialization contracts of the public Pydantic models."""

import datetime

from factories import mailing_list_json, subscriber_json

from listmonk import models


def test_subscriber_dump_reduces_lists_to_ids():
    sub = models.Subscriber(**subscriber_json(lists=[{'id': 1, 'name': 'Main'}, {'id': 3, 'name': 'Friends'}]))
    assert sub.model_dump()['lists'] == [1, 3]


def test_subscriber_dump_formats_datetimes_for_the_api():
    sub = models.Subscriber(**subscriber_json(updated_at=None))
    dumped = sub.model_dump()
    assert dumped['created_at'] == '2025-01-15T10:30:00.000000Z'
    assert dumped['updated_at'] is None


def test_mailing_list_maps_the_unconfirmed_count():
    lst = models.MailingList(**mailing_list_json(subscriber_statuses={'unconfirmed': 5}))
    assert lst.subscriber_statuses is not None
    assert lst.subscriber_statuses.unconfirmed_count == 5


def test_update_campaign_model_drops_a_past_send_at():
    past = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    model = models.UpdateCampaignModel(template_id=1, send_at=past)
    assert model.send_at is None


def test_update_campaign_model_keeps_a_future_send_at():
    future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    model = models.UpdateCampaignModel(template_id=1, send_at=future)
    assert model.send_at == future
    assert model.model_dump()['send_at'] == future.astimezone().isoformat()
