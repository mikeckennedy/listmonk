from listmonk import impl
from listmonk import models  # noqa: F401, E402
from listmonk.impl import is_healthy  # noqa: F401, E402
from listmonk.impl import lists, list_by_id  # noqa: F401, E402
from listmonk.impl import login, verify_login  # noqa: F401, E402
from listmonk.impl import set_url_base, get_base_url  # noqa: F401, E402
from listmonk.impl import subscribers, subscriber_by_email, subscriber_by_id, subscriber_by_uuid  # noqa: F401, E402

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__version__ = impl.__version__
user_agent = impl.user_agent

__all__ = [
    models,
    login, verify_login,
    set_url_base, get_base_url,
    lists, list_by_id,
    subscribers, subscriber_by_email, subscriber_by_id, subscriber_by_uuid,
    is_healthy,
]
