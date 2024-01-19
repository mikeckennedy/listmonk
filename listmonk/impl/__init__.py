import sys
import urllib.parse
from base64 import b64encode
from typing import Optional

import httpx

from listmonk import models, urls  # noqa: F401

__version__ = '0.1.0'

url_base: Optional[str] = None
username: Optional[str] = None
password: Optional[str] = None

user_agent = (f'Listmonk-Client v{__version__} / '
              f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} / '
              f'{sys.platform.capitalize()}')

core_headers: dict[str, Optional[str]] = {
    'Authorization': None,  # Set at login
    'Content-Type': 'application/json',
    'User-Agent': user_agent,
}


def set_url_base(url: str):
    if not url or not url.strip():
        raise Exception("URL must not be empty")

    global url_base
    url_base = url.strip()


def login(user_name: str, pw: str):
    global core_headers, username, password

    validate_login(user_name, pw)
    username = user_name
    password = pw

    user_pass = f'{user_name}:{pw}'.encode()
    user_pass_encoded = b64encode(user_pass).decode()

    core_headers['Authorization'] = f'Basic {user_pass_encoded}'
    if not verify_login():
        core_headers['Authorization'] = None
        return False

    return True


def lists() -> list[models.MailingList]:
    global core_headers
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.lists}?page=1&per_page=1000000'
    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    data = resp.json()
    list_of_lists = [models.MailingList(**d) for d in data.get('data', {}).get('results', [])]
    return list_of_lists


def list_by_id(list_id: int) -> Optional[models.MailingList]:
    global core_headers
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.lst}'
    url = url.format(list_id=list_id)

    resp = httpx.get(url, headers=core_headers, follow_redirects=True, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    lst_data = data.get('data')
    return models.MailingList(**lst_data)


def subscribers(query_text: Optional[str] = None) -> list[models.Subscriber]:
    global core_headers
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.subscribers}?page=1&per_page=1000'
    print(url)
    if query_text:
        url += f"&query={urllib.parse.urlencode({'query': query_text})}"

    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    # For paging:
    # data: {"total":55712,"per_page":10,"page":1, ...}

    data = resp.json()
    subscriber_list = [models.Subscriber(**d) for d in data.get('data', {}).get('results', [])]

    return subscriber_list


def is_healthy() -> bool:
    # noinspection PyBroadException
    try:
        validate_state(url=True, user=True)

        url = f'{url_base}{urls.health}'
        resp = httpx.get(url, headers=core_headers, follow_redirects=True)
        resp.raise_for_status()

        data = resp.json()
        return data.get('data', False)
    except Exception:
        return False


def verify_login() -> bool:
    return is_healthy()


def validate_login(user_name, pw):
    if not user_name:
        raise Exception("Username cannot be empty")
    if not pw:
        raise Exception("Password cannot be empty")


def validate_state(url=False, user=False):
    if url and not url_base:
        raise Exception("URL Base must be set to proceed.")

    if user and core_headers.get('Authorization') is None:
        raise Exception("You must login before proceeding.")
