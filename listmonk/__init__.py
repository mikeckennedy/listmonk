from listmonk import impl
from listmonk import models  # noqa: F401, E402
from listmonk.impl import lists, list_by_id  # noqa: F401, E402
from listmonk.impl import login, verify_login  # noqa: F401, E402
from listmonk.impl import set_url_base  # noqa: F401, E402
from listmonk.impl import subscribers  # noqa: F401, E402

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__version__ = impl.__version__
user_agent = impl.user_agent

__all__ = [
    models,
    login, verify_login,
    set_url_base,
    lists, list_by_id,
    subscribers
]
