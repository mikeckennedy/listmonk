import sys
import urllib.parse
from base64 import b64encode
from typing import Optional, Tuple

import httpx

from listmonk import models, urls  # noqa: F401

__version__ = '0.1.3'

from listmonk.models import SubscriberStatuses

# region global vars
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


# endregion

# region def get_base_url() -> Optional[str]

def get_base_url() -> Optional[str]:
    return url_base


# endregion

# region def set_url_base(url: str)

def set_url_base(url: str):
    if not url or not url.strip():
        raise Exception("URL must not be empty")

    global url_base
    url_base = url.strip()


# endregion

# region def login(user_name: str, pw: str)

def login(user_name: str, pw: str):
    global core_headers, username, password

    if not url_base or not url_base.strip():
        raise Exception("base_url must be set before you can call login.")

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


# endregion

# region def lists() -> list[models.MailingList]

def lists() -> list[models.MailingList]:
    global core_headers
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.lists}?page=1&per_page=1000000'
    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    data = resp.json()
    list_of_lists = [models.MailingList(**d) for d in data.get('data', {}).get('results', [])]
    return list_of_lists


# endregion

# region def list_by_id(list_id: int) -> Optional[models.MailingList]

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


# endregion

# region def subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None) -> list[models.Subscriber]

def subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None) -> list[models.Subscriber]:
    global core_headers
    validate_state(url=True, user=True)

    raw_results = []
    page_num = 1
    partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text)
    raw_results.extend(partial_results)
    print(f"subscribers(): Got {len(raw_results)} so far, more? {more}")
    while more:
        page_num += 1
        partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text)
        raw_results.extend(partial_results)
        print(f"subscribers(): Got {len(raw_results)} so far on page {page_num}, more? {more}")

    subscriber_list = [models.Subscriber(**d) for d in raw_results]

    return subscriber_list


# endregion

# region def _fragment_of_subscribers(page_num: int, list_id: Optional[int], query_text: Optional[str])

def _fragment_of_subscribers(page_num: int, list_id: Optional[int], query_text: Optional[str]) \
        -> Tuple[list[dict], bool]:
    """
    Returns:
        Tuple of partial_results, more_to_retrieve
    """
    per_page = 500

    url = f'{url_base}{urls.subscribers}?page={page_num}&per_page={per_page}&order_by=updated_at&order=DESC'

    if list_id:
        url += f'&list_id={list_id}'

    if query_text:
        url += f"&query={urllib.parse.urlencode({'query': query_text})}"

    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    # For paging:
    # data: {"total":55712,"per_page":10,"page":1, ...}
    raw_data = resp.json()
    data = raw_data['data']

    total = data.get('total', 0)
    retrieved = per_page * page_num
    more = retrieved < total

    local_results = data.get('results', [])
    return local_results, more


# endregion

# region def subscriber_by_email(email: str) -> Optional[models.Subscriber]

def subscriber_by_email(email: str) -> Optional[models.Subscriber]:
    global core_headers
    validate_state(url=True, user=True)

    encoded_email = email.replace('+', '%2b')
    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.email='{encoded_email}'"

    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def subscriber_by_id(subscriber_id: int) -> Optional[models.Subscriber]

def subscriber_by_id(subscriber_id: int) -> Optional[models.Subscriber]:
    global core_headers
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.id={subscriber_id}"

    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region subscriber_by_uuid(subscriber_uuid: str) -> Optional[models.Subscriber]

def subscriber_by_uuid(subscriber_uuid: str) -> Optional[models.Subscriber]:
    global core_headers
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.uuid='{subscriber_uuid}'"

    resp = httpx.get(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def create_subscriber(email: str, name: str, list_ids: set[int], pre_confirm: bool, attribs: dict)
# -> models.Subscriber

def create_subscriber(email: str, name: str, list_ids: set[int],
                      pre_confirm: bool, attribs: dict) -> models.Subscriber:
    global core_headers
    validate_state(url=True, user=True)
    email = (email or '').lower().strip()
    name = (name or '').strip()
    if not email:
        raise ValueError("Email is required")
    if not name:
        raise ValueError("Name is required")

    model = models.CreateSubscriberModel(email=email, name=name, status='enabled', lists=list(list_ids),
                                         preconfirm_subscriptions=pre_confirm, attribs=attribs)

    url = f"{url_base}{urls.subscribers}"
    resp = httpx.post(url, json=model.model_dump(), headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    # pprint(raw_data)
    sub_data = raw_data['data']
    return models.Subscriber(**sub_data)


# endregion

# region def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None) -> bool

def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None) -> bool:
    global core_headers
    validate_state(url=True, user=True)
    email = (email or '').lower().strip()
    if not email and not overriding_subscriber_id:
        raise ValueError("Email is required")

    subscriber_id = overriding_subscriber_id
    if not subscriber_id:
        subscriber = subscriber_by_email(email)
        if not subscriber:
            return False
        subscriber_id = subscriber.id

    url = f"{url_base}{urls.subscriber.format(subscriber_id=subscriber_id)}"
    resp = httpx.delete(url, headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    return raw_data.get('data')  # {'data': True}


# endregion


# region def confirm_optin(subscriber_uuid: str, list_uuid: str) -> bool

def confirm_optin(subscriber_uuid: str, list_uuid: str) -> bool:
    global core_headers
    validate_state(url=True, user=True)
    if not subscriber_uuid:
        raise ValueError("subscriber_uuid is required")
    if not list_uuid:
        raise ValueError("list_uuid is required")

    #
    # If there is a better endpoint / API for this, please let me know.
    # We're reduced to basically submitting the form via web scraping.
    #
    payload = {
        'l': list_uuid,
        'confirm': 'true',

    }
    url = f"{url_base}{urls.opt_in.format(subscriber_uuid=subscriber_uuid)}"
    resp = httpx.post(url, data=payload, follow_redirects=True)
    resp.raise_for_status()

    success_phrases = {
        # New conformation was created now.
        'Subscribed successfully.',
        'Confirmed',

        # They were already confirmed somehow previously.
        'no subscriptions to confirm',
        'No subscriptions'
    }

    text = resp.text or ''
    return any(p in text for p in success_phrases)


# endregion


# region def update_subscriber(subscriber: models.Subscriber, add_to_lists: set[int], remove_from_lists: set[int])

def update_subscriber(subscriber: models.Subscriber, add_to_lists: set[int] = None, remove_from_lists: set[int] = None,
                      status: SubscriberStatuses = SubscriberStatuses.enabled) -> models.Subscriber:
    global core_headers
    validate_state(url=True, user=True)
    if subscriber is None or not subscriber.id:
        raise ValueError("Subscriber is required")

    add_to_lists = add_to_lists or set()
    remove_from_lists = remove_from_lists or set()

    existing_lists = set([int(lst.get('id')) for lst in subscriber.lists])
    final_lists = (existing_lists - remove_from_lists)
    final_lists.update(add_to_lists)

    update_model = models.CreateSubscriberModel(
        email=subscriber.email,
        name=subscriber.name,
        status=status,
        lists=list(final_lists),
        preconfirm_subscriptions=True,
        attribs=subscriber.attribs
    )

    url = f"{url_base}{urls.subscriber.format(subscriber_id=subscriber.id)}"
    resp = httpx.put(url, json=update_model.model_dump(), headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    return subscriber_by_id(subscriber.id)


# endregion

def disable_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    return update_subscriber(subscriber, status=SubscriberStatuses.disabled)


def enable_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    return update_subscriber(subscriber, status=SubscriberStatuses.enabled)


def block_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    return update_subscriber(subscriber, status=SubscriberStatuses.blocklisted)


# region def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None) -> bool

def send_transactional_email(subscriber_email: str, template_id: int, from_email: str, template_data: dict,
                             messenger_channel: str = 'email', content_type: str = 'markdown') -> bool:
    global core_headers
    validate_state(url=True, user=True)
    subscriber_email = (subscriber_email or '').lower().strip()
    if not subscriber_email:
        raise ValueError("Email is required")

    body_data = {
        'subscriber_email': subscriber_email,
        'from_email': from_email,
        'template_id': template_id,
        'data': template_data,
        'messenger': messenger_channel,
        'content_type': content_type,
    }
    try:
        url = f"{url_base}{urls.send_tx}"
        resp = httpx.post(url, json=body_data, headers=core_headers, follow_redirects=True)
        resp.raise_for_status()

        raw_data = resp.json()
        return raw_data.get('data')  # {'data': True}
    except Exception:
        # print(e)
        # print(resp.text)
        raise


# endregion


# region def is_healthy() -> bool

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


# endregion

# region def verify_login() -> bool
def verify_login() -> bool:
    return is_healthy()


# endregion

# region def validate_login(user_name, pw)

def validate_login(user_name, pw):
    if not user_name:
        raise Exception("Username cannot be empty")
    if not pw:
        raise Exception("Password cannot be empty")


# endregion

# region def validate_state(url=False, user=False)

def validate_state(url=False, user=False):
    if url and not url_base:
        raise Exception("URL Base must be set to proceed.")

    if user and core_headers.get('Authorization') is None:
        raise Exception("You must login before proceeding.")

# endregion
