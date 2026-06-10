"""Tests for template operations through the public API."""

import pytest
from factories import template_json

import listmonk
from listmonk import models

pytestmark = pytest.mark.usefixtures('logged_in')

CONTENT_PLACEHOLDER = '{{ template "content" . }}'


def test_templates_returns_all_templates(fake_server):
    # Unlike other collection endpoints, templates come back as a flat list under 'data'.
    fake_server.respond('GET', '/api/templates', json={'data': [template_json(), template_json(id=4, type='tx')]})

    result = listmonk.templates()

    assert [t.id for t in result] == [3, 4]
    assert result[1].type == 'tx'


def test_template_by_id_returns_the_template(fake_server):
    fake_server.respond('GET', '/api/templates/3', json={'data': template_json()})

    template = listmonk.template_by_id(3)

    assert template is not None
    assert template.name == 'Welcome Email'


def test_template_by_id_returns_none_when_missing(fake_server):
    fake_server.respond('GET', '/api/templates/99', json={'data': {}})
    assert listmonk.template_by_id(99) is None


def test_template_preview_returns_the_rendered_html(fake_server):
    fake_server.respond('GET', '/api/templates/3/preview', text='<p>Lorem ipsum</p>')
    assert listmonk.template_preview_by_id(3).preview == '<p>Lorem ipsum</p>'


def test_create_template_posts_payload(fake_server):
    fake_server.respond('POST', '/api/templates', json={'data': template_json(id=9, name='Receipts', type='tx')})

    template = listmonk.create_template('Receipts', f'<header/> {CONTENT_PLACEHOLDER} <footer/>', type='tx')

    assert template.id == 9
    payload = fake_server.last_request.json
    assert payload['name'] == 'Receipts'
    assert payload['type'] == 'tx'
    assert CONTENT_PLACEHOLDER in payload['body']


def test_create_template_requires_the_content_placeholder(fake_server):
    with pytest.raises(ValueError, match='placeholder'):
        listmonk.create_template('Broken', '<p>No content marker here</p>')
    assert fake_server.requests == []


@pytest.mark.parametrize('name, body', [('', 'body'), ('   ', 'body'), ('Name', '')])
def test_create_template_requires_name_and_body(fake_server, name, body):
    with pytest.raises(ValueError):
        listmonk.create_template(name, body)
    assert fake_server.requests == []


def test_update_template_saves_then_refetches(fake_server):
    template = models.Template(**template_json())
    template.name = 'Welcome v2'
    fake_server.respond('PUT', '/api/templates/3', json={'data': True})
    fake_server.respond('GET', '/api/templates/3', json={'data': template_json(name='Welcome v2')})

    updated = listmonk.update_template(template)

    put = next(r for r in fake_server.requests if r.method == 'PUT')
    assert put.json['name'] == 'Welcome v2'
    assert updated is not None
    assert updated.name == 'Welcome v2'


def test_update_template_requires_a_saved_template(fake_server):
    with pytest.raises(ValueError):
        listmonk.update_template(models.Template(**template_json(id=0)))


def test_delete_template_deletes_an_existing_template(fake_server):
    fake_server.respond('GET', '/api/templates/3', json={'data': template_json()})
    fake_server.respond('DELETE', '/api/templates/3', json={'data': True})

    assert listmonk.delete_template(3) is True


def test_delete_template_returns_false_when_missing(fake_server):
    fake_server.respond('GET', '/api/templates/99', json={'data': {}})

    assert listmonk.delete_template(99) is False

    assert [r.method for r in fake_server.requests] == ['GET']


def test_set_default_template_promotes_an_existing_template(fake_server):
    fake_server.respond('GET', '/api/templates/3', json={'data': template_json()})
    fake_server.respond('PUT', '/api/templates/3/default', json={'data': True})

    assert listmonk.set_default_template(3) is True


def test_set_default_template_returns_false_when_missing(fake_server):
    fake_server.respond('GET', '/api/templates/99', json={'data': {}})
    assert listmonk.set_default_template(99) is False
