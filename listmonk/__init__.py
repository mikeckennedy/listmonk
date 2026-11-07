"""Listmonk Email API Client for Python.

A client for the self-hosted Listmonk email platform (https://listmonk.app), covering
subscriber management, mailing lists, campaigns, templates, and transactional email.

Typical usage:

    >>> import listmonk
    >>> listmonk.set_url_base('https://listmonk.your.domain')
    >>> listmonk.login('admin', 'super-secret')
    True
    >>> sub = listmonk.subscriber_by_email('some_user@example.com')

Entry points:

- Functions live directly on this module (``listmonk.subscribers()``, ``listmonk.create_campaign()``).
  Call ``set_url_base()`` and then ``login()`` once before any of them; auth is module-level state.
- ``listmonk.models`` holds the Pydantic models and the ``SubscriberStatuses`` / ``CampaignStatuses`` enums.
- ``listmonk.errors`` holds ``ValidationError``, ``OperationNotAllowedError``, and
  ``ListmonkFileNotFoundError``. HTTP failures raise ``httpx2.HTTPStatusError``.
- Every network call accepts ``timeout_config=httpx2.Timeout(...)`` (default 10 seconds).
- TLS trust follows the ``SSL_CERT_FILE`` / ``SSL_CERT_DIR`` environment variables.

Full documentation: https://mkennedy.codes/docs/listmonk/
"""

from listmonk import (
    errors,
    impl,
    models,
)
from listmonk.impl import (
    add_subscribers_to_lists,
    block_subscriber,
    campaign_by_id,
    campaign_preview_by_id,
    campaigns,
    cancel_campaign,
    confirm_optin,
    create_campaign,
    create_list,
    create_subscriber,
    create_template,
    delete_campaign,
    delete_list,
    delete_subscriber,
    delete_template,
    disable_subscriber,
    enable_subscriber,
    get_base_url,
    is_healthy,
    list_by_id,
    lists,
    login,
    pause_campaign,
    send_transactional_email,
    set_campaign_status,
    set_default_template,
    set_url_base,
    start_campaign,
    subscriber_by_email,
    subscriber_by_id,
    subscriber_by_uuid,
    subscribers,
    template_by_id,
    template_preview_by_id,
    templates,
    test_campaign,
    update_campaign,
    update_list,
    update_subscriber,
    update_template,
    upload_media,
    verify_login,
)

__author__: str = 'Michael Kennedy <michael@talkpython.fm>'
__version__: str = impl.__version__
user_agent: str = impl.user_agent

__all__ = [
    'errors',
    'models',
    'login',
    'verify_login',
    'set_url_base',
    'get_base_url',
    'lists',
    'list_by_id',
    'subscribers',
    'subscriber_by_email',
    'subscriber_by_id',
    'subscriber_by_uuid',
    'create_subscriber',
    'add_subscribers_to_lists',
    'delete_subscriber',
    'update_subscriber',
    'disable_subscriber',
    'enable_subscriber',
    'block_subscriber',
    'send_transactional_email',
    'confirm_optin',
    'is_healthy',
    'campaigns',
    'campaign_by_id',
    'campaign_preview_by_id',
    'create_campaign',
    'delete_campaign',
    'update_campaign',
    'set_campaign_status',
    'start_campaign',
    'pause_campaign',
    'cancel_campaign',
    'test_campaign',
    'templates',
    'create_template',
    'template_by_id',
    'template_preview_by_id',
    'delete_template',
    'update_template',
    'set_default_template',
    'create_list',
    'delete_list',
    'update_list',
    'upload_media',
]
