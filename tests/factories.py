"""Builders for JSON payloads shaped like real Listmonk API responses."""

from typing import Any, Optional


def page_json(results: list[dict[str, Any]], total: Optional[int] = None, page: int = 1) -> dict[str, Any]:
    """Wrap results in the paged envelope Listmonk uses for collection endpoints."""
    return {
        'data': {
            'results': results,
            'total': total if total is not None else len(results),
            'per_page': 500,
            'page': page,
        }
    }


def subscriber_json(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        'id': 42,
        'created_at': '2025-01-15T10:30:00.000000Z',
        'updated_at': '2025-06-01T08:00:00.000000Z',
        'uuid': 'c37786af-e6ab-4260-9b49-740a8cd6a7ed',
        'email': 'pat@example.com',
        'name': 'Pat Example',
        'attribs': {'city': 'Portland'},
        'status': 'enabled',
        'lists': [{'id': 1, 'name': 'Main Newsletter', 'subscription_status': 'confirmed'}],
    }
    data.update(overrides)
    return data


def mailing_list_json(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        'id': 1,
        'created_at': '2024-11-02T09:00:00.000000Z',
        'updated_at': '2025-05-20T12:00:00.000000Z',
        'uuid': '1bd64aa5-9b46-4566-8abd-7c7a0671e1d3',
        'name': 'Main Newsletter',
        'type': 'private',
        'optin': 'single',
        'tags': ['newsletter'],
        'description': 'The main list.',
        'subscriber_count': 1250,
        'subscriber_statuses': {'unconfirmed': 0, 'confirmed': 1250},
    }
    data.update(overrides)
    return data


def campaign_json(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        'id': 7,
        'created_at': '2025-03-10T15:04:05.000000Z',
        'updated_at': '2025-03-11T15:04:05.000000Z',
        'views': 120,
        'clicks': 30,
        'lists': [{'id': 1, 'name': 'Main Newsletter'}],
        'started_at': None,
        'to_send': 1500,
        'sent': 0,
        'uuid': '52ce9034-1cd7-4e0a-9b34-79331186cb89',
        'name': 'June Newsletter',
        'type': 'regular',
        'subject': 'Our June Update',
        'from_email': 'Newsletter <news@example.com>',
        'body': '# Big news\n\nHello there!',
        'altbody': None,
        'send_at': None,
        'status': 'draft',
        'content_type': 'markdown',
        'tags': ['newsletter'],
        'template_id': 1,
        'messenger': 'email',
        'headers': [],
        'media': [],
    }
    data.update(overrides)
    return data


def template_json(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        'id': 3,
        'created_at': '2024-12-01T10:00:00.000000Z',
        'updated_at': None,
        'name': 'Welcome Email',
        'subject': 'Welcome aboard!',
        'body': '<header/> {{ template "content" . }} <footer/>',
        'type': 'campaign',
        'is_default': False,
    }
    data.update(overrides)
    return data


def media_json(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        'id': 11,
        'uuid': '0a06fa5a-cd54-4eb6-87cf-87b8c6a04a17',
        'filename': 'logo.png',
        'content_type': 'image/png',
        'created_at': '2025-05-05T08:30:00.000000Z',
        'uri': '/uploads/logo.png',
        'thumb_uri': '/uploads/thumb_logo.png',
    }
    data.update(overrides)
    return data
