"""Tests for media uploads and transactional email through the public API."""

import json

import pytest
from factories import media_json

import listmonk
from listmonk.errors import ListmonkFileNotFoundError

pytestmark = pytest.mark.usefixtures('logged_in')


def test_upload_media_from_a_path(fake_server, tmp_path):
    logo = tmp_path / 'logo.png'
    logo.write_bytes(b'\x89PNG fake image bytes')
    fake_server.respond('POST', '/api/media', json={'data': media_json()})

    media = listmonk.upload_media(logo)

    assert media.id == 11
    assert media.uri == '/uploads/logo.png'
    field_name, (sent_name, sent_bytes) = fake_server.last_request.files[0]
    assert field_name == 'file'
    assert sent_name == 'logo.png'
    assert sent_bytes == b'\x89PNG fake image bytes'
    # Multipart requests must let httpx2 set the content type (with its boundary).
    assert 'Content-Type' not in fake_server.last_request.headers


def test_upload_media_from_bytes_with_a_filename(fake_server):
    fake_server.respond('POST', '/api/media', json={'data': media_json(filename='chart.png')})

    media = listmonk.upload_media(b'raw image bytes', filename='chart.png')

    assert media.filename == 'chart.png'
    _, (sent_name, sent_bytes) = fake_server.last_request.files[0]
    assert sent_name == 'chart.png'
    assert sent_bytes == b'raw image bytes'


def test_upload_media_bytes_require_a_filename(fake_server):
    with pytest.raises(ValueError):
        listmonk.upload_media(b'raw image bytes')
    assert fake_server.requests == []


def test_upload_media_path_must_exist(fake_server, tmp_path):
    with pytest.raises(ListmonkFileNotFoundError):
        listmonk.upload_media(tmp_path / 'missing.png')
    assert fake_server.requests == []


def test_upload_media_rejects_other_types(fake_server):
    with pytest.raises(TypeError):
        listmonk.upload_media('/tmp/logo.png')  # type: ignore[arg-type]
    assert fake_server.requests == []


def test_send_transactional_email_posts_the_message(fake_server):
    fake_server.respond('POST', '/api/tx', json={'data': True})

    ok = listmonk.send_transactional_email(
        ' Person@Example.COM ',
        template_id=3,
        from_email='mk@talkpython.fm',
        template_data={'name': 'Sam'},
        content_type='html',
        altbody='Plain text version',
    )

    assert ok is True
    payload = fake_server.last_request.json
    assert payload['subscriber_email'] == 'person@example.com'
    assert payload['template_id'] == 3
    assert payload['data'] == {'name': 'Sam'}
    assert payload['content_type'] == 'html'
    assert payload['from_email'] == 'mk@talkpython.fm'
    assert payload['altbody'] == 'Plain text version'


def test_send_transactional_email_omits_unset_optional_fields(fake_server):
    fake_server.respond('POST', '/api/tx', json={'data': True})

    listmonk.send_transactional_email('person@example.com', template_id=3)

    payload = fake_server.last_request.json
    assert 'from_email' not in payload
    assert 'altbody' not in payload


def test_send_transactional_email_requires_a_recipient(fake_server):
    with pytest.raises(ValueError):
        listmonk.send_transactional_email('   ', template_id=3)
    assert fake_server.requests == []


def test_send_transactional_email_attachments_must_exist(fake_server, tmp_path):
    missing = tmp_path / 'missing.pdf'
    with pytest.raises(ListmonkFileNotFoundError):
        listmonk.send_transactional_email('person@example.com', template_id=3, attachments=[missing])
    assert fake_server.requests == []


def test_send_transactional_email_with_attachment_switches_to_multipart(fake_server, tmp_path):
    report = tmp_path / 'report.pdf'
    report.write_bytes(b'%PDF fake report')
    fake_server.respond('POST', '/api/tx', json={'data': True})

    assert listmonk.send_transactional_email('person@example.com', template_id=3, attachments=[report]) is True

    request = fake_server.last_request
    assert request.json is None  # the message moves into multipart form data
    message = json.loads(request.data['data'])
    assert message['subscriber_email'] == 'person@example.com'
    assert message['template_id'] == 3
    field_name, (sent_name, _file_obj) = request.files[0]
    assert field_name == 'file'
    assert sent_name == 'report.pdf'
    assert 'Content-Type' not in request.headers
