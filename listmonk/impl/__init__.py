import datetime
import json
import sys
import typing
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple

import httpx

from listmonk import models, urls  # noqa: F401

__version__ = "0.3.4"

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
    "Content-Type": "application/json",
    "User-Agent": user_agent,
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
    validate_state(url=True)

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
    validate_state(url=True)

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

    # This seems to be a bug, and we'll just work around it until listmonk fixes it
    # See https://github.com/knadh/listmonk/issues/2117
    results: list[models.MailingList] = lst_data.get("results", None)
    if results:
        found = False
        lst: dict[str, typing.Any]
        for lst in results:
            if lst.get("id", "NO_VALUE") == list_id:
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
    """ # noqa
    global core_headers
    validate_state(url=True)

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
    validate_state(url=True)

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
    validate_state(url=True)

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
    Retrieves the subscriber by uuid (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed")
    Args:
        subscriber_uuid: UUID of the subscriber (e.g. "c37786af-e6ab-4260-9b49-740aaaa6ed")
    Returns: The subscribe if found, None otherwise.
    """
    global core_headers
    validate_state(url=True)

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
    validate_state(url=True)
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
    validate_state(url=True)
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
    resp = httpx.delete(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
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
    validate_state(url=True)
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
    validate_state(url=True)
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
        url,
        auth=(username, password),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
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
    """  # noqa
    global core_headers
    validate_state(url=True)
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
            # automatically by httpx including the correct boundary parameter
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
        validate_state(url=True)

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


def validate_state(url=False):
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


# region def campaigns() -> list[models.Campaign]


def campaigns() -> list[models.Campaign]:
    """
    Get campaigns on the server.
    Returns: List of Campaign objects with the full details of that campaign.
    """
    validate_state(url=True)

    url = f"{url_base}{urls.campaigns}?page=1&per_page=1000000"
    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    data = resp.json()
    list_of_campaigns = [
        models.Campaign(**d) for d in data.get("data", {}).get("results", [])
    ]
    return list_of_campaigns


# endregion

# region def campaign_by_id(campaign_id: int) -> Optional[models.Campaign]


def campaign_by_id(campaign_id: int) -> Optional[models.Campaign]:
    """
    Get the full details of a campaign with the given ID.
    Args:
        campaign_id: A campaign to get the details about, e.g. 7.
    Returns: Campaign object with the full details of a campaign.
    """
    global core_headers
    validate_state(url=True)

    url = f"{url_base}{urls.campaign_id}"
    url = url.format(campaign_id=campaign_id)

    resp = httpx.get(
        url,
        auth=(username, password),
        headers=core_headers,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()

    data = resp.json()
    campaign_data = data.get("data")

    return models.Campaign(**campaign_data)


# endregion


# region def campaign_preview_by_id(campaign_id: int) -> Optional[models.CampaignPreview]


def campaign_preview_by_id(campaign_id: int) -> Optional[models.CampaignPreview]:
    """
    Get the preview of a campaign with the given ID.
    Args:
        campaign_id: A campaign to get the details about, e.g. 7.
    Returns: String preview of the campaign.
    """
    global core_headers
    validate_state(url=True)

    url = f"{url_base}{urls.campaign_id_preview}"
    url = url.format(campaign_id=campaign_id)

    resp = httpx.get(
        url,
        auth=(username, password),
        headers=core_headers,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()
    preview = resp.text

    return models.CampaignPreview(preview=preview)


# endregion

# region def create_campaign(...) -> Optional[models.CreateCampaignModel]  # noqa: F401, E402


def create_campaign(
    name: Optional[str] = None,
    subject: Optional[str] = None,
    list_ids: set[int] = None,
    from_email: Optional[str] = None,
    campaign_type: Optional[str] = None,
    content_type: Optional[str] = None,
    body: Optional[str] = None,
    alt_body: Optional[str] = None,
    send_at: Optional[datetime.datetime] = None,
    messenger: Optional[str] = None,
    template_id: Optional[int] = None,
    tags: list[str] = None,  # noqa
    headers=None,  # noqa
) -> Optional[models.Campaign]:
    """

    Create a new campaign with the given parameters.

    Parameters:
        name (Optional[str]): The name of the campaign.
        subject (Optional[str]): The subject of the campaign.
        list_ids (set[int]): A set of list IDs to send the campaign to. Defaults to 1.
        from_email (Optional[str]): 'From' email in campaign emails. Defaults to value from settings if not provided.
        campaign_type (Optional[str]): The type of the campaign: 'regular' or 'optin'.
        content_type (Optional[str]): The content type of the campaign: 'richtext', 'html', 'markdown', 'plain'.
        body (Optional[str]): The body of the campaign.
        alt_body (Optional[str]): The alternative text body of the campaign.
        send_at (Optional[datetime.datetime]): Timestamp to schedule campaign.
        messenger (Optional[str]): The messenger for the campaign. Usually 'email'
        template_id (int): The template ID to be used for the campaign. Defaults to 1.
        tags (list[str]): A list of tags for the campaign.
        headers (list[dict]): A list of headers for the campaign.

    Returns:
        CreateCampaignModel: A model representing the created campaign.

    Raises:
        ValueError: If required parameters (name, subject, from_email) are not provided.

    """
    if headers is None:
        headers = []
    if tags is None:
        tags = []

    validate_state(url=True)
    from_email = (from_email or "").lower().strip()
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")
    if not subject:
        raise ValueError("Subject is required")
    if list_ids is None:  # The Default list is 1.
        list_ids = [1]

    model = models.CreateCampaignModel(
        name=name,
        subject=subject,
        lists=list_ids,
        from_email=from_email,
        type=campaign_type,
        content_type=content_type,
        body=body,
        altbody=alt_body,
        send_at=send_at,
        messenger=messenger,
        template_id=template_id,
        tags=tags,
        headers=headers,
    )
    url = f"{url_base}{urls.campaigns}"
    resp = httpx.post(
        url,
        auth=(username, password),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
    )
    resp.raise_for_status()

    raw_data = resp.json()
    campaign_data = raw_data["data"]
    return models.Campaign(**campaign_data)


# endregion

# region def delete_campaign(campaign_id: Optional[str] = None) -> bool


def delete_campaign(campaign_id: Optional[int] = None) -> bool:
    """
    Completely delete a campaign from your system.

    Args:
        campaign_id: name of the campaign to delete.
    Returns: True if the campaign was successfully deleted, False otherwise.
    """
    global core_headers
    validate_state(url=True)

    if not campaign_id:
        raise ValueError("Campaign ID is required")

    campaign = campaign_by_id(campaign_id)
    if not campaign:
        return False

    url = f"{url_base}{urls.campaign_id.format(campaign_id=campaign_id)}"
    resp = httpx.delete(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    return raw_data.get("data")  # Looks like {'data': True}


# endregion

# region def update_campaign(campaign: models.Campaign)


def update_campaign(
    campaign: models.Campaign,
) -> models.Campaign:
    """

    Update the given campaign with the provided campaign information.

    Parameters:
    - campaign: models.Campaign - The campaign object containing the updated information.

    Returns:
    - models.Campaign - The updated campaign object from api.

    Raises:
    - ValueError: If the campaign parameter is None or if the campaign id is not present.

    """
    global core_headers
    validate_state(url=True)
    if campaign is None or not campaign.id:
        raise ValueError("Campaign is required")

    update_lists = [item['id'] if isinstance(item, dict) else item for item in campaign.lists]

    update_model = models.UpdateCampaignModel(
        name=campaign.name,
        subject=campaign.subject,
        lists=update_lists,
        from_email=campaign.from_email,
        type=campaign.type,
        content_type=campaign.content_type,
        body=campaign.body,
        altbody=campaign.altbody,
        send_at=campaign.send_at,
        messenger=campaign.messenger,
        template_id=campaign.template_id,
        tags=campaign.tags,
        headers=campaign.headers,
    )

    url = f"{url_base}{urls.campaign_id.format(campaign_id=campaign.id)}"
    resp = httpx.put(
        url,
        auth=(username, password),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
    )
    resp.raise_for_status()

    return campaign_by_id(campaign.id)


# endregion


# region def templates() -> list[models.Template]


def templates() -> list[models.Template]:
    """
    This function retrieves a list of all templates available in the system.

    Returns:
        list of models.Template objects representing the templates available in the system.
    """
    validate_state(url=True)

    url = f"{url_base}{urls.templates}?page=1&per_page=1000000"
    resp = httpx.get(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    data = resp.json()
    list_of_templates = [
        models.Template(**d) for d in data.get("data", [])
    ]
    return list_of_templates


# endregion


# region def create_template(...) -> Optional[models.CreateTemplateModel]  # noqa: F401, E402


def create_template(
        name: Optional[str] = None,
        body: Optional[str] = None,
        type: Optional[str] = None,
        is_default: Optional[bool] = None,
) -> Optional[models.Template]:
    """
    Create a template with the specified details.

    Parameters:
        name (Optional[str]): The name of the template.
        body (Optional[str]): The body content of the template.
        type (Optional[str]): The type of the template.
        is_default (Optional[bool]): Indicates if the template is the default one.

    Returns:
        Optional[models.Template]: An instance of models.Template representing the created template.
    """
    validate_state(url=True)
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")
    if not body:
        raise ValueError("Body is required")
    if """{{ template "content" . }}""" not in body:
        raise ValueError("""The placeholder {{ template "content" . }} should appear exactly once in the template.""")

    model = models.CreateTemplateModel(
        name=name,
        body=body,
        type=type,
        is_default=is_default,
    )

    url = f"{url_base}{urls.templates}"
    resp = httpx.post(
        url,
        auth=(username, password),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
    )
    resp.raise_for_status()

    raw_data = resp.json()
    template_data = raw_data["data"]
    return models.Template(**template_data)


# endregion


# region def template_by_id(template_id: int) -> Optional[models.template]


def template_by_id(template_id: int) -> Optional[models.Template]:
    """
    Retrieve a template by its ID.

    Parameters:
    template_id (int): The ID of the template to retrieve.

    Returns:
    Optional[models.Template]: The template object retrieved based on the ID provided.
    """
    global core_headers
    validate_state(url=True)

    url = f"{url_base}{urls.template_id}"
    url = url.format(template_id=template_id)

    resp = httpx.get(
        url,
        auth=(username, password),
        headers=core_headers,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()

    data = resp.json()
    template_data = data.get("data")

    return models.Template(**template_data)


# endregion

# region def template_preview_by_id(template_id: int) -> Optional[models.TemplatePreview]


def template_preview_by_id(template_id: int) -> Optional[models.TemplatePreview]:
    """
    Get the preview of a template with the given ID.
    Args:
        template_id: A campaign to get the details about, e.g. 7.
    Returns: String preview of the template with lorem ipsum.
    """
    global core_headers
    validate_state(url=True)

    url = f"{url_base}{urls.template_id_preview}"
    url = url.format(template_id=template_id)

    resp = httpx.get(
        url,
        auth=(username, password),
        headers=core_headers,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()
    preview = resp.text

    return models.TemplatePreview(preview=preview)


# endregion


# region def delete_template(template_id: Optional[str] = None) -> bool


def delete_template(template_id: Optional[int] = None) -> bool:
    """
    Completely delete a template from your system.

    Args:
        template_id: name of the template to delete.
    Returns: True if the template was successfully deleted, False otherwise.
    """
    global core_headers
    validate_state(url=True)

    if not template_id:
        raise ValueError("Template ID is required")

    template = template_by_id(template_id)
    if not template:
        return False

    url = f"{url_base}{urls.template_id.format(template_id=template_id)}"
    resp = httpx.delete(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    return raw_data.get("data")  # Looks like {'data': True}


# endregion


# region def update_template(template: models.Template)


def update_template(
    template: models.Template,
) -> models.Template:
    """

        Update a template in the system.

        Parameters:
            template: models.Template - the template object to be updated

        Returns:
            models.Template - the updated template object after the update operation

    """
    global core_headers
    validate_state(url=True)
    if template is None or not template.id:
        raise ValueError("Template is required")

    update_model = models.CreateTemplateModel(
        name=template.name,
        body=template.body,
        type=template.type,
    )

    url = f"{url_base}{urls.template_id.format(template_id=template.id)}"
    resp = httpx.put(
        url,
        auth=(username, password),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
    )
    resp.raise_for_status()

    return template_by_id(template.id)


# endregion


# region def set_default_template(template_id: Optional[str] = None) -> bool


def set_default_template(template_id: Optional[int] = None) -> bool:
    """

    Set the given template ID as the default template.

    Parameters:
        template_id (Optional[int]): The ID of the template to set as default. If not provided, a ValueError is raised.

    Returns:
        bool: True if the default template was set successfully, False otherwise.

    """
    global core_headers
    validate_state(url=True)

    if not template_id:
        raise ValueError("Template ID is required")

    template = template_by_id(template_id)
    if not template:
        return False

    url = f"{url_base}{urls.template_id_default.format(template_id=template_id)}"
    resp = httpx.put(
        url, auth=(username, password), headers=core_headers, follow_redirects=True
    )
    resp.raise_for_status()

    raw_data = resp.json()
    return raw_data.get("data")  # Looks like {'data': True}


# endregion
