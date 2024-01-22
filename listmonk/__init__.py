from listmonk import impl
from listmonk import models  # noqa: F401, E402
from listmonk.impl import confirm_optin  # noqa: F401, E402
from listmonk.impl import create_subscriber, delete_subscriber, update_subscriber  # noqa: F401, E402
from listmonk.impl import disable_subscriber, enable_subscriber, block_subscriber  # noqa: F401, E402
from listmonk.impl import is_healthy  # noqa: F401, E402
from listmonk.impl import lists, list_by_id  # noqa: F401, E402
from listmonk.impl import login, verify_login  # noqa: F401, E402
from listmonk.impl import send_transactional_email  # noqa: F401, E402
from listmonk.impl import set_url_base, get_base_url  # noqa: F401, E402
from listmonk.impl import subscribers, subscriber_by_email, subscriber_by_id, subscriber_by_uuid  # noqa: F401, E402

__author__: str = 'Michael Kennedy <michael@talkpython.fm>'
__version__: str = impl.__version__
user_agent: str = impl.user_agent

__all__ = [
    models,
    login, verify_login,
    set_url_base, get_base_url,
    lists, list_by_id,
    subscribers, subscriber_by_email, subscriber_by_id, subscriber_by_uuid,
    create_subscriber, delete_subscriber, update_subscriber,
    disable_subscriber, enable_subscriber, block_subscriber,
    send_transactional_email,
    confirm_optin,
    is_healthy,
]
