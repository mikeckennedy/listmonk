import json
import sys
import urllib.parse
from base64 import b64encode
from pathlib import Path
from typing import Optional, Tuple

import httpx

from listmonk import models, urls  # noqa: F401

__version__ = "0.2.0"

from listmonk.errors import ValidationError, OperationNotAllowedError, FileNotFoundError

from listmonk.models import SubscriberStatuses

# region global vars
url_base: Optional[str] = None
username: Optional[str] = None
password: Optional[str] = None
has_logged_in: bool = False

user_agent: str = (
    f"Listmonk-Client v{__version__} / "
    f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} / "
    f"{sys.platform.capitalize()}"
)

core_headers: dict[str, Optional[str]] = {
    'Content-Type': 'application/json',
    'User-Agent': user_agent,
}


# endregion

# region def get_base_url() -> Optional[str]


def get_base_url() -> Optional[str]:
    """
    Each Listmonk instance lives somewhere. This is where yours lives.
    For example, https://listmonk.somedomain.tech.

    Returns: The base URL of your instance.
    """
    return url_base


# endregion

# region def set_url_base(url: str)


def set_url_base(url: str):
    """
    Each Listmonk instance lives somewhere. This is where yours lives.
    For example, https://listmonk.somedomain.tech.
    Args:
        url: The base URL of your instance without /api.
    """
    if not url or not url.strip():
        raise ValidationError("URL must not be empty.")

    # noinspection HttpUrlsUsage
    if not url.startswith("http://") and not url.startswith("https://"):
        # noinspection HttpUrlsUsage
        raise ValidationError(
            "The url must start with the HTTP scheme (http:// or https://)."
        )

    if url.endswith("/"):
        url = url.rstrip("/")

    global url_base
    url_base = url.strip()


# endregion

# region def login(user_name: str, pw: str)


def login(user_name: str, pw: str) -> bool:
    """
    Logs into Listmonk and stores that authentication for the life of your app.
    Args:
        user_name: Your Listmonk username
        pw: Your Listmonk password

    Returns: Returns a boolean indicating whether the login was successful.
    """

    global has_logged_in, username, password

    if not url_base or not url_base.strip():
        raise OperationNotAllowedError(
            "base_url must be set before you can call login."
        )

    validate_login(user_name, pw)
    username = user_name
    password = pw

    has_logged_in = test_user_pw_on_server()

    return has_logged_in


# endregion

# region def lists() -> list[models.MailingList]


def lists() -> list[models.MailingList]:
    """
    Get mailing lists on the server.
    Returns: List of MailingList objects with the full details of that list.
    """
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.lists}?page=1&per_page=1000000"
    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    data = resp.json()
    list_of_lists = [
        models.MailingList(**d) for d in data.get("data", {}).get("results", [])
    ]
    return list_of_lists


# endregion

# region def list_by_id(list_id: int) -> Optional[models.MailingList]


def list_by_id(list_id: int) -> Optional[models.MailingList]:
    """
    Get the full details of a list with the given ID.
    Args:
        list_id: A list to get the details about, e.g. 7.
    Returns: MailingList object with the full details of a list.
    """
    global core_headers
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.lst}"
    url = url.format(list_id=list_id)

    resp = httpx.get(
        url,
        auth=(username, password),
        headers=core_headers,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()

    data = resp.json()
    lst_data = data.get("data")

    # This seems to be a bug and we'll just work around it until listmonk fixes it
    # See https://github.com/knadh/listmonk/issues/2117
    results: list[models.MailingList] = lst_data.get('results', None)
    if results:
        found = False
        for lst in results:
            if lst.get('id', 'NO_VALUE') == list_id:
                lst_data = lst
                found = True
                break

        if not found:
            raise Exception(f"List with ID {list_id} not found.")

    return models.MailingList(**lst_data)


# endregion

# region def subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None) -> list[models.Subscriber]


def subscribers(
    query_text: Optional[str] = None, list_id: Optional[int] = None
) -> list[models.Subscriber]:
    """
    Get a list of subscribers matching the criteria provided. If none, then all subscribers are returned.
    Args:
        query_text: Custom query text such as "subscribers.attribs->>'city' = 'Portland'". See the full documentation at https://listmonk.app/docs/querying-and-segmentation/
        list_id: Pass a list ID and get the subscribers, matching the query, from that list.
    Returns: A list of subscribers matching the criteria provided. If none, then all subscribers are returned.
    """
    global core_headers
    validate_state(url=True, user=True)

    raw_results = []
    page_num = 1
    partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text)
    raw_results.extend(partial_results)
    # Logging someday: print(f"subscribers(): Got {len(raw_results)} so far, more? {more}")
    while more:
        page_num += 1
        partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text)
        raw_results.extend(partial_results)
        # Logging someday: print(f"subscribers(): Got {len(raw_results)} so far on page {page_num}, more? {more}")

    subscriber_list = [models.Subscriber(**d) for d in raw_results]

    return subscriber_list


# endregion

# region def _fragment_of_subscribers(page_num: int, list_id: Optional[int], query_text: Optional[str])


def _fragment_of_subscribers(
    page_num: int, list_id: Optional[int], query_text: Optional[str]
) -> Tuple[list[dict], bool]:
    """
    Internal use only.
    Returns:
        Tuple of partial_results, more_to_retrieve
    """
    per_page = 500

    url = f"{url_base}{urls.subscribers}?page={page_num}&per_page={per_page}&order_by=updated_at&order=DESC"

    if list_id:
        url += f"&list_id={list_id}"

    if query_text:
        url += f"&{urllib.parse.urlencode({'query': query_text})}"

    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    # For paging:
    # data: {"total":55712,"per_page":10,"page":1, ...}
    raw_data = resp.json()
    data = raw_data["data"]

    total = data.get("total", 0)
    retrieved = per_page * page_num
    more = retrieved < total

    local_results = data.get("results", [])
    return local_results, more


# endregion

# region def subscriber_by_email(email: str) -> Optional[models.Subscriber]


def subscriber_by_email(email: str) -> Optional[models.Subscriber]:
    """
    Retrieves the subscribe by email (e.g. "some_user@talkpython.fm")
    Args:
        email: Email of the subscriber (e.g. "some_user@talkpython.fm")
    Returns: The subscribe if found, None otherwise.
    """
    global core_headers
    validate_state(url=True, user=True)

    encoded_email = email.replace("+", "%2b")
    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.email='{encoded_email}'"

    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data["data"]["results"]

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def subscriber_by_id(subscriber_id: int) -> Optional[models.Subscriber]


def subscriber_by_id(subscriber_id: int) -> Optional[models.Subscriber]:
    """
    Retrieves the subscribe by id (e.g. 201)
    Args:
        subscriber_id: ID of the subscriber (e.g. 201)
    Returns: The subscribe if found, None otherwise.
    """
    global core_headers
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.id={subscriber_id}"

    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data["data"]["results"]

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region subscriber_by_uuid(subscriber_uuid: str) -> Optional[models.Subscriber]


def subscriber_by_uuid(subscriber_uuid: str) -> Optional[models.Subscriber]:
    """
    Retrieves the subscribe by uuid (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed")
    Args:
        subscriber_uuid: UUID of the subscriber (e.g. "c37786af-e6ab-4260-9b49-740aaaa6ed")
    Returns: The subscribe if found, None otherwise.
    """
    global core_headers
    validate_state(url=True, user=True)

    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.uuid='{subscriber_uuid}'"

    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    results: list[dict] = raw_data["data"]["results"]

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def create_subscriber(email: str, name: str, list_ids: set[int], pre_confirm: bool, attribs: dict)


def create_subscriber(
    email: str, name: str, list_ids: set[int], pre_confirm: bool, attribs: dict
) -> models.Subscriber:
    """
    Create a new subscriber on the Listmonk server.
    Args:
        email: Email of the subscriber.
        name: Full name (first[SPACE]last) of the subscriber
        list_ids: List of list IDs for the lists to add them to (say that 3 times fast!)
        pre_confirm: Whether to preconfirm the subscriber for double opt-in lists (no email to them)
        attribs: Custom dictionary for the attribs data on the user record (queryable in the subscriber UI).
    Returns: The Subscribe object that was created on the server with ID, UUID, and much more.
    """
    global core_headers
    validate_state(url=True, user=True)
    email = (email or "").lower().strip()
    name = (name or "").strip()
    if not email:
        raise ValueError("Email is required")
    if not name:
        raise ValueError("Name is required")

    model = models.CreateSubscriberModel(
        email=email,
        name=name,
        status="enabled",
        lists=list(list_ids),
        preconfirm_subscriptions=pre_confirm,
        attribs=attribs,
    )

    url = f"{url_base}{urls.subscribers}"
    resp = httpx.post(
        url,
        auth=(username, password),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
    )
    resp.raise_for_status()

    raw_data = resp.json()
    # pprint(raw_data)
    sub_data = raw_data["data"]
    return models.Subscriber(**sub_data)


# endregion

# region def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None) -> bool


def delete_subscriber(
    email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None
) -> bool:
    """
    Completely delete a subscriber from your system (it's as if they were never there).
    If your goal is to unsubscribe them, then use the block_subscriber method.
    Args:
        email: Email of the account to delete.
        overriding_subscriber_id:  Optional ID of the account to delete (takes precedence).
    Returns: True if they were successfully deleted, False otherwise.
    """
    global core_headers
    validate_state(url=True, user=True)
    email = (email or "").lower().strip()
    if not email and not overriding_subscriber_id:
        raise ValueError("Email is required")

    subscriber_id = overriding_subscriber_id
    if not subscriber_id:
        subscriber = subscriber_by_email(email)
        if not subscriber:
            return False
        subscriber_id = subscriber.id

    url = f"{url_base}{urls.subscriber.format(subscriber_id=subscriber_id)}"
    resp = httpx.delete(url, auth=(username, password), headers=core_headers, follow_redirects=True)
    resp.raise_for_status()

    raw_data = resp.json()
    return raw_data.get("data")  # Looks like {'data': True}


# endregion

# region def confirm_optin(subscriber_uuid: str, list_uuid: str) -> bool


def confirm_optin(subscriber_uuid: str, list_uuid: str) -> bool:
    """
    For opt-in situations, subscribers are added as unconfirmed first. This method will opt them in
    via the API. You should only do this when they are actually opting in. If you have your own opt-in
    form, but it's via your code, then this makes sense.
    Args:
        subscriber_uuid: The Subscriber.uuid value for the subscriber.
        list_uuid: The MailingList.uuid value for the list.
    Returns: True if they were successfully opted in.
    """
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
        "l": list_uuid,
        "confirm": "true",
    }
    url = f"{url_base}{urls.opt_in.format(subscriber_uuid=subscriber_uuid)}"
    resp = httpx.post(
        url, auth=(username, password), data=payload, follow_redirects=True
    )
    resp.raise_for_status()

    success_phrases = {
        # New conformation was created now.
        "Subscribed successfully.",
        "Confirmed",
        # They were already confirmed somehow previously.
        "no subscriptions to confirm",
        "No subscriptions",
    }

    text = resp.text or ""
    return any(p in text for p in success_phrases)


# endregion

# region def update_subscriber(subscriber: models.Subscriber, add_to_lists: set[int], remove_from_lists: set[int])


def update_subscriber(
    subscriber: models.Subscriber,
    add_to_lists: set[int] = None,
    remove_from_lists: set[int] = None,
    status: SubscriberStatuses = SubscriberStatuses.enabled,
) -> models.Subscriber:
    """
    Update many aspects of a subscriber, from their email addresses and names, to custom attribute data, and
    from adding them to and removing them from lists. You can enable, disable, and block them here. But if that
    is all you want tod o there are functions dedicated to that which are simpler.
    Args:
        subscriber: The full subscriber object to update (with changed fields and values)
        add_to_lists: Any list to add to this subscriber to.
        remove_from_lists: Any list to remove from this subscriber.
        status: The status of the subscriber: enabled, disabled, blacklisted from SubscriberStatuses.
    Returns: The updated view of the subscriber object from the server.
    """
    global core_headers
    validate_state(url=True, user=True)
    if subscriber is None or not subscriber.id:
        raise ValueError("Subscriber is required")

    add_to_lists = add_to_lists or set()
    remove_from_lists = remove_from_lists or set()

    existing_lists = set([int(lst.get("id")) for lst in subscriber.lists])
    final_lists = existing_lists - remove_from_lists
    final_lists.update(add_to_lists)

    update_model = models.CreateSubscriberModel(
        email=subscriber.email,
        name=subscriber.name,
        status=status,
        lists=list(final_lists),
        preconfirm_subscriptions=True,
        attribs=subscriber.attribs,
    )

    url = f"{url_base}{urls.subscriber.format(subscriber_id=subscriber.id)}"
    resp = httpx.put(
        url, auth=(username, password), json=update_model.model_dump(), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    return subscriber_by_id(subscriber.id)


# endregion

# region def disable_subscriber(subscriber: models.Subscriber) -> models.Subscriber


def disable_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    """
    Set a subscriber's status to disable.
    Args:
        subscriber: The subscriber to disable.
    Returns: The updated subscriber object from the server.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.disabled)


# endregion

# region def enable_subscriber(subscriber: models.Subscriber) -> models.Subscriber


def enable_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    """
    Set a subscriber's status to enable.
    Args:
        subscriber: The subscriber to enable.
    Returns: The updated subscriber object from the server.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.enabled)


# endregion

# region def block_subscriber(subscriber: models.Subscriber) -> models.Subscriber


def block_subscriber(subscriber: models.Subscriber) -> models.Subscriber:
    """
    Add a subscriber to the blocklist, AKA unsubscribe them.
    Args:
        subscriber: The subscriber to block/unsubscribe.
    Returns: The updated subscriber object from the server.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.blocklisted)


# endregion

# region def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None) -> bool


def send_transactional_email(
    subscriber_email: str,
    template_id: int,
    from_email: Optional[str] = None,
    template_data: Optional[dict] = None,
    messenger_channel: str = "email",
    content_type: str = "markdown",
    attachments: Optional[list[Path]] = None,
) -> bool:
    """
    Send a transactional email through Listmonk to the recipient.
    Args:
        subscriber_email: The email address to send the email to (they must be a subscriber of *some* list on your server).
        template_id: The template ID to use for the email. It must be a "transactional" not campaign template.
        from_email: The from address for the email. Can be omitted to use default email at your output provider.
        template_data: A dictionary of merge parameters for the template, available in the template as {{ .Tx.Data.* }}.
        messenger_channel: Default is "email", if you have SMS or some other channel, you can use it here.
        content_type: Email format options include html, markdown, and plain.
        attachments: Optional list of `pathlib.Path` objects pointing to file that will be sent as attachment.
    Returns: True if the email send was successful, False otherwise. Errors may show up in the logs section of your Listmonk dashboard.
    """
    global core_headers
    validate_state(url=True, user=True)
    subscriber_email = (subscriber_email or "").lower().strip()
    if not subscriber_email:
        raise ValueError("Email is required")

    # Verify attachments
    if attachments is not None:
        for attachment in attachments:
            if not attachment.exists() or not attachment.is_file():
                raise FileNotFoundError(f"Attachment {attachment} does not exist")

    body_data = {
        "subscriber_email": subscriber_email,
        "template_id": template_id,
        "data": template_data or {},
        "messenger": messenger_channel,
        "content_type": content_type,
    }

    if from_email is not None:
        body_data["from_email"] = from_email

    try:
        url = f"{url_base}{urls.send_tx}"

        # Depending on existence of attachments, we need to send data in different ways
        if attachments:
            # Multiple files can be uploaded in one go as per the advanced httpx docs
            # https://www.python-httpx.org/advanced/#multipart-file-encoding
            files = [
                ("file", (attachment.name, open(attachment, "rb")))
                for attachment in attachments
            ]
            # Data has to be sent as form field named data as per the listmonk API docs
            # https://listmonk.app/docs/apis/transactional/#file-attachments
            data = {
                "data": json.dumps(body_data, ensure_ascii=False).encode("utf-8"),
            }
            # Need to remove content type header as it should not be JSON and is set
            # automatically by httpx including the correct boundary paramter
            headers = core_headers.copy()
            headers.pop("Content-Type")

            resp = httpx.post(
                url,
                auth=(username, password),
                data=data,
                files=files,
                headers=headers,
                follow_redirects=True,
            )
        else:
            resp = httpx.post(
                url,
                auth=(username, password),
                json=body_data,
                headers=core_headers,
                follow_redirects=True,
            )

        resp.raise_for_status()

        raw_data = resp.json()
        return raw_data.get("data")  # {'data': True}
    except Exception:
        # Maybe some logging here at some point.
        raise


# endregion

# region def is_healthy() -> bool


def is_healthy() -> bool:
    """
    Checks that the token retrieved during login is still valid at your server.
    Returns: True if the token is still valid, False otherwise.
    """
    # noinspection PyBroadException
    try:
        validate_state(url=True, user=True)

        url = f"{url_base}{urls.health}"
        resp = httpx.get(
            url, auth=(username, password), headers=core_headers, follow_redirects=True
        )
        resp.raise_for_status()

        data = resp.json()
        return data.get("data", False)
    except Exception:
        return False


# endregion


# region def verify_login() -> bool
def verify_login() -> bool:
    """
    Call to verify that the stored auth token is still valid.
    Returns: True if the stored auth token is still value, False otherwise.
    """
    return is_healthy()


# endregion

# region def validate_login(user_name, pw)


def validate_login(user_name, pw):
    """
    Internal use only.
    """
    if not user_name:
        raise ValidationError("Username cannot be empty")
    if not pw:
        raise ValidationError("Password cannot be empty")


# endregion

# region def validate_state(url=False, user=False)


def validate_state(url=False, user=False):
    """
    Internal use only.
    """
    if url and not url_base:
        raise OperationNotAllowedError("URL Base must be set to proceed.")

    if not has_logged_in:
        raise OperationNotAllowedError("You must login before proceeding.")


# endregion


def test_user_pw_on_server() -> bool:
    if has_logged_in:
        return True

    # noinspection PyBroadException
    try:
        url = f"{url_base}{urls.health}"
        resp = httpx.get(
            url, auth=(username, password), headers=core_headers, follow_redirects=True
        )
        # resp2 = requests.get(url, auth=(username, password))
        resp.raise_for_status()

        return True
    except Exception:
        return False
