import datetime
import json
import sys
import typing
import urllib.parse
from importlib.metadata import version
from pathlib import Path
from typing import Any, Optional, Tuple

import httpx2

from listmonk import models, urls

__version__ = version('listmonk')

from listmonk.errors import ListmonkFileNotFoundError, OperationNotAllowedError, ValidationError
from listmonk.models import SubscriberStatuses

# region global vars
url_base: Optional[str] = None
username: Optional[str] = None
password: Optional[str] = None
has_logged_in: bool = False

user_agent: str = (
    f'Listmonk-Client v{__version__} / '
    f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} / '
    f'{sys.platform.capitalize()}'
)

core_headers: dict[str, str] = {
    'Content-Type': 'application/json',
    'User-Agent': user_agent,
}


# endregion


def _validate_and_parse_json_response(resp: httpx2.Response) -> dict[str, Any]:
    """
    Internal helper to validate HTTP response and parse JSON with proper error handling.

    Args:
        resp: The httpx2 Response object

    Returns:
        Parsed JSON data as dictionary

    Raises:
        httpx2.HTTPStatusError: If the response status is 4xx or 5xx.
        ValidationError: If response is empty or contains invalid JSON
    """
    resp.raise_for_status()

    if not resp.content:
        raise ValidationError('Empty response from server')

    try:
        return resp.json()
    except (ValueError, json.JSONDecodeError) as e:
        raise ValidationError(f'Invalid JSON response from server: {e}')


# region def get_base_url() -> Optional[str]


def get_base_url() -> Optional[str]:
    """
    Return the configured base URL of your Listmonk instance.

    Each Listmonk instance lives at its own address, for example
    https://listmonk.somedomain.tech. This getter returns whatever value was
    previously stored by set_url_base().

    Returns:
        The base URL of your instance (without a trailing slash), or None if
        set_url_base() has not been called yet.
    """
    return url_base


# endregion


# region def set_url_base(url: str)


def set_url_base(url: str) -> None:
    """
    Set the base URL of your Listmonk instance for all subsequent calls.

    Each Listmonk instance lives at its own address, for example
    https://listmonk.somedomain.tech. This must be called before login() and
    any other API operation. A trailing slash, if present, is removed.

    Args:
        url: The base URL of your instance, including the http:// or https://
            scheme but without the /api path segment.

    Raises:
        ValidationError: If url is empty or whitespace, or if it does not
            start with the http:// or https:// scheme.
    """
    if not url or not url.strip():
        raise ValidationError('URL must not be empty.')

    # noinspection HttpUrlsUsage
    if not url.startswith('http://') and not url.startswith('https://'):
        # noinspection HttpUrlsUsage
        raise ValidationError('The url must start with the HTTP scheme (http:// or https://).')

    if url.endswith('/'):
        url = url.rstrip('/')

    global url_base
    url_base = url.strip()


# endregion


# region def login(user_name: str, pw: str, timeout_config: Optional[httpx2.Timeout] = None) -> bool


def login(user_name: str, pw: str, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Log into Listmonk and cache the credentials for the life of your app.

    The username and password are validated against the server's health
    endpoint using HTTP Basic auth. On success they are stored in module-level
    state and reused by every subsequent API call, so you only need to call
    this once. set_url_base() must be called first.

    Args:
        user_name: Your Listmonk username.
        pw: Your Listmonk password.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the credentials were accepted by the server. Returns False if
        the server rejected them or could not be reached (no HTTP error is
        raised in that case).

    Raises:
        OperationNotAllowedError: If the base URL has not been set via
            set_url_base().
        ValidationError: If user_name or pw is empty.

    Examples:
        >>> import listmonk
        >>> listmonk.set_url_base('https://listmonk.somedomain.tech')
        >>> listmonk.login('admin', 'super-secret')
        True
    """

    global has_logged_in, username, password

    if not url_base or not url_base.strip():
        raise OperationNotAllowedError('base_url must be set before you can call login.')

    validate_login(user_name, pw)
    username = user_name
    password = pw

    # Reset so repeat login() calls re-validate the new credentials against the
    # server instead of hitting the has_logged_in short-circuit in
    # test_user_pw_on_server().
    has_logged_in = False
    has_logged_in = test_user_pw_on_server(timeout_config)

    return has_logged_in


# endregion

# region def lists(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.MailingList]


def lists(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.MailingList]:
    """
    Get all mailing lists on the server.

    Retrieves every mailing list in a single request (paged at one large page),
    so no manual pagination is required.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A list of MailingList objects with the full details of each list. Returns
        an empty list if the server has no mailing lists.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        ValidationError: If the server returns an empty or invalid JSON response.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    # noinspection DuplicatedCode
    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    url = f'{url_base}{urls.lists}?page=1&per_page=1000000'
    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    list_of_lists = [models.MailingList(**d) for d in data.get('data', {}).get('results', [])]
    return list_of_lists


# endregion


# region def list_by_id(list_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.MailingList


def list_by_id(list_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.MailingList:
    """
    Get the full details of a single mailing list by its ID.

    Args:
        list_id: The numeric ID of the list to retrieve, e.g. 7.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A MailingList object with the full details of the requested list.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        ValidationError: If the server returns an empty or invalid JSON response.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        Exception: If the server returns a result set that does not contain the
            requested list_id (a workaround for a known Listmonk server quirk).
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.lst}'
    url = url.format(list_id=list_id)

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    lst_data = data.get('data', {})

    # This seems to be a bug, and we'll just work around it until listmonk fixes it
    # See https://github.com/knadh/listmonk/issues/2117
    results: list[dict[str, Any]] = lst_data.get('results', [])
    if results:
        found = False
        for lst in results:
            if lst['id'] == list_id:
                lst_data = lst
                found = True
                break

        if not found:
            raise Exception(f'List with ID {list_id} not found.')

    return models.MailingList(**lst_data)  # type: ignore


# endregion

# region def subscribers(query_text: Optional[str] = None, list_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> list[models.Subscriber]  # noqa: E501


def subscribers(
    query_text: Optional[str] = None, list_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None
) -> list[models.Subscriber]:
    """
    Get the list of subscribers matching the given criteria, or all subscribers if no criteria are given.

    Results are fetched page by page (500 per page) and combined, so a broad query may issue
    several HTTP requests and return a large list. Subscribers are ordered by ``updated_at`` descending.

    Args:
        query_text: Optional SQL-like filter applied server-side, e.g.
            ``"subscribers.attribs->>'city' = 'Portland'"``. See
            https://listmonk.app/docs/querying-and-segmentation/ for the syntax. Defaults to None (no filter).
        list_id: Optional list ID; when given, only subscribers belonging to that list
            (and matching ``query_text``, if any) are returned. Defaults to None.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A list of models.Subscriber objects matching the criteria. Returns an empty list
        (never None) if nothing matches.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        ValidationError: If the server returns an empty body or invalid JSON.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    raw_results = []
    page_num = 1
    partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text, timeout_config)
    raw_results.extend(partial_results)  # type: ignore
    # Logging someday: print(f"subscribers(): Got {len(raw_results)} so far, more? {more}")
    while more:
        page_num += 1
        partial_results, more = _fragment_of_subscribers(page_num, list_id, query_text, timeout_config)
        raw_results.extend(partial_results)  # type: ignore
        # Logging someday: print(f"subscribers(): Got {len(raw_results)} so far on page {page_num}, more? {more}")

    subscriber_list = [models.Subscriber(**d) for d in raw_results]  # type: ignore

    return subscriber_list


# endregion

# region def _fragment_of_subscribers(page_num: int, list_id: Optional[int], query_text: Optional[str], timeout_config: Optional[httpx2.Timeout] = None) -> Tuple[list[dict[str, Any]], bool]  # noqa: E501


def _fragment_of_subscribers(
    page_num: int, list_id: Optional[int], query_text: Optional[str], timeout_config: Optional[httpx2.Timeout] = None
) -> Tuple[list[dict[str, Any]], bool]:
    """
    Internal use only.

    Returns:
        Tuple of partial_results, more_to_retrieve
    """
    per_page = 500
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    url = f'{url_base}{urls.subscribers}?page={page_num}&per_page={per_page}&order_by=updated_at&order=DESC'

    if list_id:
        url += f'&list_id={list_id}'

    if query_text:
        url += f'&{urllib.parse.urlencode({"query": query_text})}'

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    # For paging:
    # data: {"total":55712,"per_page":10,"page":1, ...}
    raw_data = _validate_and_parse_json_response(resp)
    data = raw_data['data']

    total = data.get('total', 0)
    retrieved = per_page * page_num
    more = retrieved < total

    local_results = data.get('results', [])
    return local_results, more


# endregion

# region def subscriber_by_email(email: str, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def subscriber_by_email(email: str, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]:
    """
    Retrieve a single subscriber by their email address (e.g. "some_user@talkpython.fm").

    The email is matched exactly against ``subscribers.email`` on the server (a ``+`` in the
    address is URL-encoded automatically), and the first matching subscriber is returned.

    Args:
        email: Email address of the subscriber to look up (e.g. "some_user@talkpython.fm").
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The matching models.Subscriber, or None if no subscriber has that email.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        ValidationError: If the server returns an empty body or invalid JSON.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    encoded_email = email.replace('+', '%2b')
    # noinspection DuplicatedCode
    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.email='{encoded_email}'"

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    results: list[dict[str, Any]] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])  # type: ignore


# endregion

# region def subscriber_by_id(subscriber_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def subscriber_by_id(
    subscriber_id: int, timeout_config: Optional[httpx2.Timeout] = None
) -> Optional[models.Subscriber]:
    """
    Retrieve a single subscriber by their numeric Listmonk ID (e.g. 201).

    The ID is matched against ``subscribers.id`` on the server and the first matching
    subscriber is returned.

    Args:
        subscriber_id: Numeric ID of the subscriber to look up (e.g. 201).
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The matching models.Subscriber, or None if no subscriber has that ID.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        ValidationError: If the server returns an empty body or invalid JSON.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.id={subscriber_id}'

    # noinspection DuplicatedCode
    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    results: list[dict[str, Any]] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def subscriber_by_uuid(subscriber_uuid: str, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def subscriber_by_uuid(
    subscriber_uuid: str, timeout_config: Optional[httpx2.Timeout] = None
) -> Optional[models.Subscriber]:
    """
    Retrieve a single subscriber by their UUID (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed").

    The UUID is matched against ``subscribers.uuid`` on the server and the first matching
    subscriber is returned.

    Args:
        subscriber_uuid: UUID of the subscriber to look up (e.g. "c37786af-e6ab-4260-9b49-740adpcm6ed").
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The matching models.Subscriber, or None if no subscriber has that UUID.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        ValidationError: If the server returns an empty body or invalid JSON.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    # noinspection DuplicatedCode
    url = f"{url_base}{urls.subscribers}?page=1&per_page=100&query=subscribers.uuid='{subscriber_uuid}'"

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    results: list[dict[str, Any]] = raw_data['data']['results']

    if not results:
        return None

    return models.Subscriber(**results[0])


# endregion

# region def create_subscriber(
#       email: str, name: Optional[str] = None, list_ids: Optional[set[int]] = None, pre_confirm: bool = False,
#       attribs: Optional[dict[str, Any]] = None, timeout_config: Optional[httpx2.Timeout] = None
# )


def create_subscriber(
    email: str,
    name: Optional[str] = None,
    list_ids: Optional[set[int]] = None,
    pre_confirm: bool = False,
    attribs: Optional[dict[str, Any]] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> models.Subscriber:
    """
    Create a new subscriber on the Listmonk server.

    The email is lowercased and stripped and the name is stripped before the request is sent.
    The subscriber is always created with a global status of ``enabled``.

    Args:
        email: Email address of the subscriber. Required and must be non-empty after stripping.
        name: Full name (e.g. "first last") of the subscriber. Defaults to None (stored as an empty string).
        list_ids: Set of list IDs to subscribe this person to. Defaults to None (no lists).
        pre_confirm: When True, mark the new subscriptions as confirmed immediately so no
            double opt-in confirmation email is sent. Defaults to False.
        attribs: Custom attributes to store on the subscriber record (queryable in the
            subscriber UI). Defaults to None (stored as an empty dict).
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The newly created models.Subscriber, populated by the server with its ID, UUID, and more.

    Raises:
        ValueError: If email is empty.
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        ValidationError: If the server returns an empty body or invalid JSON.
        httpx2.HTTPStatusError: If the server rejects the request (e.g. a 4xx for a duplicate
            email) or returns a 5xx status.

    Examples:
        >>> import listmonk
        >>> sub = listmonk.create_subscriber(
        ...     email='some_user@talkpython.fm',
        ...     name='Some User',
        ...     list_ids={1, 4},
        ...     pre_confirm=True,
        ...     attribs={'city': 'Portland'},
        ... )
        >>> sub.id
        201
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    email = (email or '').lower().strip()
    name = (name or '').strip()
    if not email:
        raise ValueError('Email is required')
    model = models.CreateSubscriberModel(
        email=email,
        name=name or '',
        status='enabled',
        lists=list(list_ids or []),
        preconfirm_subscriptions=pre_confirm,
        attribs=attribs or {},
    )

    # noinspection DuplicatedCode
    url = f'{url_base}{urls.subscribers}'
    resp = httpx2.post(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    sub_data = raw_data['data']
    return models.Subscriber(**sub_data)


# endregion

# region def delete_subscriber(email: Optional[str] = None, overriding_subscriber_id: Optional[int] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool  # noqa: E501


def delete_subscriber(
    email: Optional[str] = None,
    overriding_subscriber_id: Optional[int] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> bool:
    """
    Completely delete a subscriber from your system (as if they were never there).

    If your goal is to unsubscribe them rather than erase them, use block_subscriber instead. The email is
    normalized (lowercased and stripped) before lookup. When both arguments are given, overriding_subscriber_id
    takes precedence.

    Args:
        email: Email of the subscriber to delete. Required unless overriding_subscriber_id is provided.
        overriding_subscriber_id: Optional ID of the subscriber to delete; takes precedence over email.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the subscriber was successfully deleted. False if no subscriber matched the given email
        (when no overriding id was provided) or if the server reported the delete as unsuccessful.

    Raises:
        ValueError: If neither email nor overriding_subscriber_id is provided.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the server returns an empty or invalid JSON response.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    email = (email or '').lower().strip()
    if not email and not overriding_subscriber_id:
        raise ValueError('Email is required')

    subscriber_id = overriding_subscriber_id
    if not subscriber_id:
        subscriber = subscriber_by_email(email, timeout_config)
        if not subscriber:
            return False
        subscriber_id = subscriber.id

    # noinspection DuplicatedCode
    url = f'{url_base}{urls.subscriber.format(subscriber_id=subscriber_id)}'
    resp = httpx2.delete(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    return bool(raw_data.get('data'))  # Looks like {'data': True}


# endregion

# region def confirm_optin(subscriber_uuid: str, list_uuid: str, timeout_config: Optional[httpx2.Timeout] = None) -> bool  # noqa: E501


def confirm_optin(subscriber_uuid: str, list_uuid: str, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Confirm a subscriber's opt-in to a list via the API.

    For opt-in lists, subscribers are added as unconfirmed first. Call this to opt them in, but only when they are
    genuinely opting in (for example, from your own opt-in form handled in your code). This submits the public
    opt-in form on the subscription endpoint rather than calling a JSON API, so HTTP errors are reported as a
    False return value rather than raised.

    Args:
        subscriber_uuid: The Subscriber.uuid value for the subscriber. Must be non-empty.
        list_uuid: The MailingList.uuid value for the list. Must be non-empty.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the opt-in succeeded, False if the server responded with a non-success status.

    Raises:
        ValueError: If subscriber_uuid or list_uuid is empty.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    if not subscriber_uuid:
        raise ValueError('subscriber_uuid is required')
    if not list_uuid:
        raise ValueError('list_uuid is required')

    #
    # If there is a better endpoint / API for this, please let me know.
    # We're reduced to basically submitting the form via web scraping.
    #
    payload = {
        'l': list_uuid,
        'confirm': 'true',
    }
    url = f'{url_base}{urls.opt_in.format(subscriber_uuid=subscriber_uuid)}'
    resp = httpx2.post(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        data=payload,
        follow_redirects=True,
        timeout=timeout_config,
    )
    try:
        resp.raise_for_status()
    except httpx2.HTTPStatusError:
        return False

    return True


# endregion

# region def add_subscribers_to_lists(subscriber_ids: typing.Iterable[int], list_ids: typing.Iterable[int], timeout_config: Optional[httpx2.Timeout] = None, status: str = 'confirmed') -> bool  # noqa: E501


def add_subscribers_to_lists(
    subscriber_ids: typing.Iterable[int],
    list_ids: typing.Iterable[int],
    timeout_config: Optional[httpx2.Timeout] = None,
    status: str = 'confirmed',
) -> bool:
    """
    Add a number of subscribers to a number of lists in a single bulk operation.

    Args:
        subscriber_ids: An iterable of subscriber IDs to add. Duplicates are de-duplicated.
        list_ids: An iterable of target list IDs to subscribe them to. Duplicates are de-duplicated.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.
        status: The subscription status to assign on the target lists, e.g. 'confirmed' or 'unconfirmed'.
            Defaults to 'confirmed'.

    Returns:
        True on success. False if either ID set is empty or contains only 0, or if the server responds with an
        error status.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    unique_subscriber_ids = set(subscriber_ids)
    unique_list_ids = set(list_ids)

    if not unique_subscriber_ids or unique_subscriber_ids.issubset({0}):
        return False

    if not unique_list_ids or unique_list_ids.issubset({0}):
        return False

    payload = {
        'ids': list(unique_subscriber_ids),
        'action': 'add',
        'target_list_ids': list(unique_list_ids),
        'status': status,
    }

    url = f'{url_base}{urls.subscriber_lists}'

    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=payload,
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )

    try:
        resp.raise_for_status()
    except Exception:
        return False

    return True


# endregion

# region def update_subscriber(subscriber: models.Subscriber, add_to_lists: Optional[set[int]] = None, remove_from_lists: Optional[set[int]] = None, status: SubscriberStatuses = SubscriberStatuses.enabled, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def update_subscriber(
    subscriber: models.Subscriber,
    add_to_lists: Optional[set[int]] = None,
    remove_from_lists: Optional[set[int]] = None,
    status: SubscriberStatuses = SubscriberStatuses.enabled,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> Optional[models.Subscriber]:
    """
    Update many aspects of a subscriber: email and name, custom attribute data, list membership, and status.

    Final list membership is computed from the subscriber's existing lists minus ``remove_from_lists`` plus
    ``add_to_lists``, and the affected subscriptions are preconfirmed. You can enable, disable, or block a subscriber
    here, but if that is all you want to do there are dedicated, simpler functions (enable_subscriber,
    disable_subscriber, block_subscriber).

    Args:
        subscriber: The full subscriber object to update, with the changed fields already set. Must have a valid id.
        add_to_lists: List IDs to add this subscriber to. Defaults to None (treated as an empty set).
        remove_from_lists: List IDs to remove this subscriber from. Defaults to None (treated as an empty set).
        status: The subscriber's status, one of SubscriberStatuses.enabled, .disabled, or .blocklisted.
            Defaults to SubscriberStatuses.enabled.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The refreshed subscriber object fetched from the server after the update, or None if the subscriber
        can no longer be found.

    Raises:
        ValueError: If subscriber is None or has no id.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the follow-up fetch returns an empty or invalid JSON response.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    if subscriber is None or not subscriber.id:
        raise ValueError('Subscriber is required')

    add_to_lists = add_to_lists or set()
    remove_from_lists = remove_from_lists or set()

    existing_lists = {int(lst['id']) for lst in subscriber.lists}  # type: ignore
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

    url = f'{url_base}{urls.subscriber.format(subscriber_id=subscriber.id)}'
    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    resp.raise_for_status()

    return subscriber_by_id(subscriber.id, timeout_config)


# endregion

# region def disable_subscriber(subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def disable_subscriber(
    subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None
) -> Optional[models.Subscriber]:
    """
    Set a subscriber's status to disabled, pausing their subscription so they will not receive campaigns.

    This is a convenience wrapper around update_subscriber that changes only the status.

    Args:
        subscriber: The subscriber to disable. Must have a valid id.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The refreshed subscriber object from the server, or None if the subscriber can no longer be found.

    Raises:
        ValueError: If subscriber is None or has no id.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the follow-up fetch returns an empty or invalid JSON response.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.disabled, timeout_config=timeout_config)


# endregion

# region def enable_subscriber(subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def enable_subscriber(
    subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None
) -> Optional[models.Subscriber]:
    """
    Set a subscriber's status to enabled so they will receive campaigns.

    This is a convenience wrapper around update_subscriber that changes only the status.

    Args:
        subscriber: The subscriber to enable. Must have a valid id.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The refreshed subscriber object from the server, or None if the subscriber can no longer be found.

    Raises:
        ValueError: If subscriber is None or has no id.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the follow-up fetch returns an empty or invalid JSON response.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.enabled, timeout_config=timeout_config)


# endregion

# region def block_subscriber(subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Subscriber]  # noqa: E501


def block_subscriber(
    subscriber: models.Subscriber, timeout_config: Optional[httpx2.Timeout] = None
) -> Optional[models.Subscriber]:
    """
    Add a subscriber to the blocklist, effectively unsubscribing them so they will not receive any mail.

    This is a convenience wrapper around update_subscriber that sets the status to SubscriberStatuses.blocklisted.
    Use delete_subscriber instead if you want to remove the subscriber record entirely.

    Args:
        subscriber: The subscriber to block/unsubscribe. Must have a valid id.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The refreshed subscriber object from the server, or None if the subscriber can no longer be found.

    Raises:
        ValueError: If subscriber is None or has no id.
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the follow-up fetch returns an empty or invalid JSON response.
    """
    return update_subscriber(subscriber, status=SubscriberStatuses.blocklisted, timeout_config=timeout_config)


# endregion

# region def send_transactional_email(subscriber_email: str, template_id: int, from_email: Optional[str] = None, template_data: Optional[dict[str, Any]] = None, messenger_channel: str = 'email', content_type: str = 'markdown', altbody: Optional[str] = None, attachments: Optional[list[Path]] = None, email_headers: Optional[list[dict[str, Optional[str]]]] = None, timeout_config: Optional[httpx2.Timeout] = None) -> bool  # noqa: E501


def send_transactional_email(
    subscriber_email: str,
    template_id: int,
    from_email: Optional[str] = None,
    template_data: Optional[dict[str, Any]] = None,
    messenger_channel: str = 'email',
    content_type: str = 'markdown',
    altbody: Optional[str] = None,
    attachments: Optional[list[Path]] = None,
    email_headers: Optional[list[dict[str, Optional[str]]]] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> bool:
    """
    Send a transactional email through Listmonk to a single recipient.

    The recipient must already be a subscriber on at least one list. Delivery
    errors may surface in the logs section of your Listmonk dashboard rather than
    as exceptions here. The subscriber_email is lowercased and stripped before sending.

    Args:
        subscriber_email: The recipient's email address. Required; they must be a
            subscriber of some list on your server.
        template_id: The ID of the template to render. Must be a 'tx'
            (transactional) template, not a campaign template.
        from_email: The From address. Omit to use the default address at your
            sending provider.
        template_data: Merge parameters available in the template as {{ .Tx.Data.* }}.
            Defaults to an empty dict.
        messenger_channel: The delivery channel. Defaults to 'email'; use another
            configured channel (e.g. SMS) if available.
        content_type: The body format: 'html', 'markdown', or 'plain'.
            Defaults to 'markdown'.
        altbody: Optional alternate plain-text body for multipart HTML emails.
        attachments: Optional list of pathlib.Path objects pointing to files to
            attach. Each path must exist and be a file.
        email_headers: Optional list of custom headers, each a single-entry dict,
            e.g. [{'X-Custom': 'value'}].
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the server accepted the send, False otherwise.

    Raises:
        ValueError: If subscriber_email is empty.
        ListmonkFileNotFoundError: If any attachment path does not exist or is not a file.
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the response is empty or is not valid JSON.

    Examples:
        >>> import listmonk
        >>> listmonk.send_transactional_email(
        ...     subscriber_email='person@example.com',
        ...     template_id=3,
        ...     template_data={'name': 'Sam'},
        ... )
        True
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    subscriber_email = (subscriber_email or '').lower().strip()
    if not subscriber_email:
        raise ValueError('Email is required')

    # Verify attachments
    if attachments is not None:
        for attachment in attachments:
            if not attachment.exists() or not attachment.is_file():
                raise ListmonkFileNotFoundError(f'Attachment {attachment} does not exist')

    body_data = {
        'subscriber_email': subscriber_email,
        'template_id': template_id,
        'data': template_data or {},
        'messenger': messenger_channel,
        'content_type': content_type,
        'headers': email_headers or [],
    }

    if from_email is not None:
        body_data['from_email'] = from_email

    if altbody is not None:
        body_data['altbody'] = altbody

    try:
        url = f'{url_base}{urls.send_tx}'

        # Depending on existence of attachments, we need to send data in different ways
        if attachments:
            # Multiple files can be uploaded in one go as per the advanced httpx docs
            # https://www.python-httpx.org/advanced/clients/#multipart-file-encoding
            files = [('file', (attachment.name, open(attachment, 'rb'))) for attachment in attachments]
            # Data has to be sent as form field named data as per the listmonk API docs
            # https://listmonk.app/docs/apis/transactional/#file-attachments
            data = {
                'data': json.dumps(body_data, ensure_ascii=False).encode('utf-8'),
            }
            # Need to remove content type header as it should not be JSON and is set
            # automatically by httpx2 including the correct boundary parameter
            headers = core_headers.copy()
            headers.pop('Content-Type')

            resp = httpx2.post(
                url,
                auth=httpx2.BasicAuth(username or '', password or ''),
                data=data,
                files=files,
                headers=headers,
                follow_redirects=True,
                timeout=timeout_config,
            )
        else:
            resp = httpx2.post(
                url,
                auth=httpx2.BasicAuth(username or '', password or ''),
                json=body_data,
                headers=core_headers,
                follow_redirects=True,
                timeout=timeout_config,
            )

        raw_data = _validate_and_parse_json_response(resp)
        return bool(raw_data.get('data'))  # {'data': True}
    except Exception:
        # Maybe some logging here at some point.
        raise


# endregion

# region def is_healthy(timeout_config: Optional[httpx2.Timeout] = None) -> bool


def is_healthy(timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Check whether the server is reachable and the stored credentials are valid.

    Issues an authenticated GET to the Listmonk health endpoint using the
    cached username and password. This call is defensive: any failure—the URL
    base not being set, not being logged in, a network error, a non-2xx
    response, or an unparseable body—is caught and reported as False, so it
    never raises.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the server responded healthy with valid credentials, False
        otherwise.
    """
    # noinspection PyBroadException
    try:
        validate_state(url=True)
        timeout_config = timeout_config or httpx2.Timeout(timeout=10)

        url = f'{url_base}{urls.health}'
        resp = httpx2.get(
            url,
            auth=httpx2.BasicAuth(username or '', password or ''),
            headers=core_headers,
            follow_redirects=True,
            timeout=timeout_config,
        )
        data = _validate_and_parse_json_response(resp)
        return data.get('data', False)
    except Exception:
        return False


# endregion


# region def verify_login(timeout_config: Optional[httpx2.Timeout] = None) -> bool
def verify_login(timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Verify that the stored login credentials are still valid at the server.

    This is a thin alias for is_healthy(): it issues an authenticated request
    to the server's health endpoint using the cached credentials. Any error
    (not logged in, network failure, rejected credentials) is reported as
    False rather than raised.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the stored credentials are still valid, False otherwise.
    """
    return is_healthy(timeout_config=timeout_config)


# endregion

# region def validate_login(user_name: str, pw: str) -> None


def validate_login(user_name: str, pw: str) -> None:
    """
    Validate that login credentials are non-empty (internal use only).

    Args:
        user_name: The username to check.
        pw: The password to check.

    Raises:
        ValidationError: If user_name is empty, or if pw is empty.
    """
    if not user_name:
        raise ValidationError('Username cannot be empty')
    if not pw:
        raise ValidationError('Password cannot be empty')


# endregion

# region def validate_state(url: bool = False) -> None


def validate_state(url: bool = False) -> None:
    """
    Ensure the client is ready to make an authenticated request (internal use only).

    Args:
        url: If True, also require that the base URL has been set; defaults to
            False.

    Raises:
        OperationNotAllowedError: If url is True and the base URL has not been
            set, or if the client has not logged in successfully.
    """
    if url and not url_base:
        raise OperationNotAllowedError('URL Base must be set to proceed.')

    if not has_logged_in:
        raise OperationNotAllowedError('You must login before proceeding.')


# endregion

# region def test_user_pw_on_server(timeout_config: Optional[httpx2.Timeout] = None) -> bool


def test_user_pw_on_server(timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Test whether the cached username/password are valid on the server (internal use only).

    Returns True immediately if a successful login has already been recorded.
    Otherwise issues an authenticated request to the health endpoint; any error
    is caught and reported as False, so it never raises.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the credentials are valid (or login was already established),
        False otherwise.
    """
    if has_logged_in:
        return True

    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    # noinspection PyBroadException
    try:
        url = f'{url_base}{urls.health}'
        resp = httpx2.get(
            url,
            auth=httpx2.BasicAuth(username or '', password or ''),
            headers=core_headers,
            follow_redirects=True,
            timeout=timeout_config,
        )
        resp.raise_for_status()

        return True
    except Exception:
        return False


# endregion

# region def campaigns(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.Campaign]


def campaigns(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.Campaign]:
    """
    Get all campaigns on the server.

    Fetches the full list of campaigns in a single request (the server is asked
    for up to one million results per page), so no pagination is required.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A list of Campaign objects, each with the full details of that campaign.
        Returns an empty list if the instance has no campaigns.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the server returns an empty body or invalid JSON.
    """
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.campaigns}?page=1&per_page=1000000'
    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    list_of_campaigns = [models.Campaign(**d) for d in data.get('data', {}).get('results', [])]
    return list_of_campaigns


# endregion

# region def campaign_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Campaign]  # noqa: E501


def campaign_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Campaign]:
    """
    Get the full details of a campaign with the given ID.

    Args:
        campaign_id: The numeric ID of the campaign to fetch, e.g. 7.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A Campaign object with the full details of the campaign, or None if the
        server returns no campaign data for the given ID.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the server returns an empty body or invalid JSON.
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.campaign_id}'
    url = url.format(campaign_id=campaign_id)

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    campaign_data = data.get('data', {})
    if not campaign_data:
        return None

    return models.Campaign(**campaign_data)


# endregion


# region def campaign_preview_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.CampaignPreview  # noqa: E501


def campaign_preview_by_id(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.CampaignPreview:
    """
    Get the rendered preview of a campaign with the given ID.

    Args:
        campaign_id: The numeric ID of the campaign to preview, e.g. 7.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A CampaignPreview object whose ``preview`` attribute holds the rendered
        HTML body returned by the server.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.campaign_id_preview}'
    url = url.format(campaign_id=campaign_id)

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    resp.raise_for_status()
    preview = resp.text

    return models.CampaignPreview(preview=preview)


# endregion

# region def create_campaign(...) -> models.Campaign


def create_campaign(
    name: str,
    subject: str,
    list_ids: Optional[set[int]] = None,
    from_email: Optional[str] = None,
    campaign_type: Optional[str] = None,
    content_type: Optional[str] = None,
    body: Optional[str] = None,
    alt_body: Optional[str] = None,
    send_at: Optional[datetime.datetime] = None,
    messenger: Optional[str] = None,
    template_id: Optional[int] = None,
    tags: Optional[list[str]] = None,
    headers: Optional[list[dict[str, Optional[str]]]] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> models.Campaign:
    """
    Create a new campaign with the given parameters.

    Name and subject are required; all other fields fall back to defaults
    (for example, ``list_ids`` defaults to the single list {1} and ``from_email``
    falls back to the instance settings when omitted).

    Args:
        name: The internal name of the campaign. Required.
        subject: The email subject line. Required.
        list_ids: A set of list IDs to send the campaign to. Defaults to {1}.
        from_email: The 'From' address for campaign emails. Defaults to the
            instance setting when not provided.
        campaign_type: The campaign type, 'regular' or 'optin'.
        content_type: The body format: 'richtext', 'html', 'markdown', or 'plain'.
        body: The campaign body in the configured content type.
        alt_body: The optional plain-text alternative body for multipart HTML emails.
        send_at: Optional timestamp at which to schedule the campaign.
        messenger: The delivery channel, usually 'email'.
        template_id: The ID of the template used to render the campaign.
        tags: A list of tags to attach to the campaign.
        headers: A list of custom email headers, each a single-entry dict.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A Campaign object with the full details of the newly created campaign.

    Raises:
        ValueError: If ``name`` is empty after stripping or ``subject`` is empty.
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the server returns an empty body or invalid JSON.

    Examples:
        >>> import listmonk
        >>> campaign = listmonk.create_campaign(
        ...     name='June Newsletter',
        ...     subject='Our June Update',
        ...     list_ids={1, 2},
        ...     content_type='html',
        ...     body='<h1>Hello</h1>',
        ... )
        >>> campaign.id
        7
    """
    if headers is None:
        headers = []
    if tags is None:
        tags = []

    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    from_email = (from_email or '').lower().strip()
    name = (name or '').strip()
    if not name:
        raise ValueError('Name is required')
    if not subject:
        raise ValueError('Subject is required')
    if list_ids is None:  # The Default list is 1.
        list_ids = {1}

    model = models.CreateCampaignModel(
        name=name,
        subject=subject,
        lists=list(list_ids),
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
    # noinspection DuplicatedCode
    url = f'{url_base}{urls.campaigns}'
    resp = httpx2.post(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    campaign_data = raw_data['data']
    return models.Campaign(**campaign_data)


# endregion

# region def delete_campaign(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool


def delete_campaign(campaign_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Completely delete a campaign from your system.

    The campaign is first looked up by ID; if no such campaign exists the
    function returns False without issuing a delete request.

    Args:
        campaign_id: The numeric ID of the campaign to delete.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the campaign was successfully deleted; False if no campaign with
        the given ID was found or the server reported it was not deleted.

    Raises:
        ValueError: If ``campaign_id`` is falsy (e.g. 0).
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the server returns an empty body or invalid JSON.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    if not campaign_id:
        raise ValueError('Campaign ID is required')

    campaign = campaign_by_id(campaign_id, timeout_config)
    # noinspection DuplicatedCode
    if not campaign:
        return False

    url = f'{url_base}{urls.campaign_id.format(campaign_id=campaign_id)}'
    resp = httpx2.delete(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    return bool(raw_data.get('data'))  # Looks like {'data': True}


# endregion

# region def update_campaign(campaign: models.Campaign, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Campaign]  # noqa: E501


def update_campaign(
    campaign: models.Campaign,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> Optional[models.Campaign]:
    """
    Update an existing campaign with the provided campaign information.

    The campaign's target lists are normalized to their IDs before sending, and
    a ``send_at`` value already in the past is dropped so the update does not
    fail on a stale scheduled time. After the update succeeds, the campaign is
    re-fetched from the server and returned.

    Args:
        campaign: The Campaign object containing the updated information. Must
            have a valid ``id``.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The updated Campaign object as freshly fetched from the server, or None
        if the campaign can no longer be found after the update.

    Raises:
        ValueError: If ``campaign`` is None or has no ``id``.
        OperationNotAllowedError: If the base URL is not set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the follow-up fetch returns an empty or invalid JSON response.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    if campaign is None or not campaign.id:  # type: ignore
        raise ValueError('Campaign is required')

    update_lists = [item['id'] if isinstance(item, dict) else item for item in campaign.lists]  # type: ignore

    update_model = models.UpdateCampaignModel(
        name=campaign.name,
        subject=campaign.subject,
        lists=list(update_lists),  # Convert to list to ensure type is known # type: ignore
        from_email=campaign.from_email,
        type=campaign.type,
        content_type=campaign.content_type,
        body=campaign.body,
        altbody=campaign.altbody,
        send_at=campaign.send_at,
        messenger=campaign.messenger,
        template_id=campaign.template_id,
        tags=campaign.tags,
        headers=campaign.headers,  # type: ignore
    )

    url = f'{url_base}{urls.campaign_id.format(campaign_id=campaign.id)}'
    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    resp.raise_for_status()

    return campaign_by_id(campaign.id, timeout_config)


# endregion


# region def templates(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.Template]


def templates(timeout_config: Optional[httpx2.Timeout] = None) -> list[models.Template]:
    """
    Retrieve all templates defined on the Listmonk instance.

    This fetches both campaign and transactional templates in a single (large)
    paginated request.

    Args:
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A list of models.Template objects, one per template on the server.
        Returns an empty list if no templates are defined.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the response is empty or is not valid JSON.
    """
    # noinspection DuplicatedCode
    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    url = f'{url_base}{urls.templates}?page=1&per_page=1000000'
    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    list_of_templates = [models.Template(**d) for d in data.get('data', [])]
    return list_of_templates


# endregion


# region def create_template(...) -> models.Template


# noinspection PyShadowingBuiltins
def create_template(
    name: str,
    body: str,
    type: Optional[str] = None,
    is_default: Optional[bool] = None,
    subject: Optional[str] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> models.Template:
    """
    Create a new template on the Listmonk instance.

    The body must contain the placeholder {{ template "content" . }} exactly where
    the rendered content should be injected; a template is rejected without it.

    Args:
        name: The template name. Required; a ValueError is raised if empty.
        body: The template body markup. Required, and must contain the
            {{ template "content" . }} placeholder.
        type: The template type, e.g. 'campaign' or 'tx' (transactional).
        is_default: Whether the new template should become the default for its type.
        subject: The default subject line for the template, if any.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A models.Template representing the newly created template.

    Raises:
        ValueError: If name is empty, if body is empty, or if body does not
            contain the {{ template "content" . }} placeholder.
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the response is empty or is not valid JSON.

    Examples:
        >>> import listmonk
        >>> body = 'Header {{ template "content" . }} Footer'
        >>> tmpl = listmonk.create_template(name='Welcome', body=body, type='tx')
        >>> tmpl.id
        7
    """
    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    name = (name or '').strip()
    if not name:
        raise ValueError('Name is required')
    if not body:
        raise ValueError('Body is required')
    if """{{ template "content" . }}""" not in body:
        raise ValueError("""The placeholder {{ template "content" . }} should appear exactly once in the template.""")

    model = models.CreateTemplateModel(
        name=name,
        subject=subject,
        body=body,
        type=type,
        is_default=is_default,
    )

    # noinspection DuplicatedCode
    url = f'{url_base}{urls.templates}'
    resp = httpx2.post(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    template_data = raw_data['data']
    return models.Template(**template_data)


# endregion


# region def template_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Template]  # noqa: E501


def template_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Template]:
    """
    Retrieve a single template by its numeric ID.

    Args:
        template_id: The numeric ID of the template to retrieve, e.g. 7.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A models.Template built from the server's response for the given ID, or
        None if the server returns no template data.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status (e.g. an unknown template ID).
        ValidationError: If the response is empty or is not valid JSON.
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.template_id}'
    url = url.format(template_id=template_id)

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    data = _validate_and_parse_json_response(resp)
    template_data = data.get('data', {})
    if not template_data:
        return None

    return models.Template(**template_data)


# endregion

# region def template_preview_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.TemplatePreview  # noqa: E501


def template_preview_by_id(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> models.TemplatePreview:
    """
    Render and return a preview of a template.

    The preview is rendered by the server using lorem-ipsum sample content, so it
    can be inspected without sending real data through the template.

    Args:
        template_id: The numeric ID of the template to preview, e.g. 7.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A models.TemplatePreview whose 'preview' field holds the rendered HTML.

    Raises:
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status (e.g. an unknown template ID).
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    url = f'{url_base}{urls.template_id_preview}'
    url = url.format(template_id=template_id)

    resp = httpx2.get(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    resp.raise_for_status()
    preview = resp.text

    return models.TemplatePreview(preview=preview)


# endregion


# region def delete_template(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool


def delete_template(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Permanently delete a template from the Listmonk instance.

    The template is first looked up by ID; if it does not exist, no delete is
    attempted and False is returned.

    Args:
        template_id: The numeric ID of the template to delete. Required.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the template was deleted successfully. False if no template with
        the given ID exists.

    Raises:
        ValueError: If template_id is falsy (e.g. 0).
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the response is empty or is not valid JSON.
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    if not template_id:
        raise ValueError('Template ID is required')

    template = template_by_id(template_id, timeout_config)
    if not template:
        return False

    url = f'{url_base}{urls.template_id.format(template_id=template_id)}'
    resp = httpx2.delete(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    return bool(raw_data.get('data'))  # Looks like {'data': True}


# endregion


# region def update_template(template: models.Template, timeout_config: Optional[httpx2.Timeout] = None) -> Optional[models.Template]  # noqa: E501


def update_template(
    template: models.Template,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> Optional[models.Template]:
    """
    Update an existing template on the Listmonk instance.

    The template's name, subject, body, and type are sent in the update; the
    is_default flag is not changed by this call (use set_default_template for that).
    After the update succeeds, the template is re-fetched and returned.

    Args:
        template: The models.Template to update. Must be non-None and have an id.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        A freshly fetched models.Template reflecting the saved changes.

    Raises:
        ValueError: If template is None or has no id.
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the re-fetch response is empty or is not valid JSON.
    """
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)
    if template is None or not template.id:  # type: ignore
        raise ValueError('Template is required')

    update_model = models.CreateTemplateModel(
        name=template.name,
        subject=template.subject,
        body=template.body,
        type=template.type,
    )

    url = f'{url_base}{urls.template_id.format(template_id=template.id)}'
    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=update_model.model_dump(),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    resp.raise_for_status()

    return template_by_id(template.id, timeout_config)


# endregion


# region def set_default_template(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool


def set_default_template(template_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Mark the given template as the default for its type.

    The template is first looked up by ID; if it does not exist, the default is
    not changed and False is returned.

    Args:
        template_id: The numeric ID of the template to set as default. Required.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the default was set successfully. False if no template with the
        given ID exists.

    Raises:
        ValueError: If template_id is falsy (e.g. 0).
        OperationNotAllowedError: If the base URL has not been set or you have not logged in.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
        ValidationError: If the response is empty or is not valid JSON.
    """
    # noinspection DuplicatedCode
    global core_headers
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    validate_state(url=True)

    if not template_id:
        raise ValueError('Template ID is required')

    template = template_by_id(template_id, timeout_config)
    if not template:
        return False

    url = f'{url_base}{urls.template_id_default.format(template_id=template_id)}'
    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    return bool(raw_data.get('data'))  # Looks like {'data': True}


# endregion


# region def create_list(list_name: str, ...) -> models.MailingList


def create_list(
    list_name: str,
    list_type: str = 'public',
    optin: str = 'single',
    tags: Optional[list[str]] = None,
    description: Optional[str] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> models.MailingList:
    """
    Create a new mailing list on the server.

    The list name is stripped of surrounding whitespace before submission.

    Args:
        list_name: Name of the new list. Required and must be non-empty after
            whitespace is stripped.
        list_type: Visibility of the list. One of 'public' or 'private'.
            Defaults to 'public'.
        optin: Opt-in mode. One of 'single' or 'double'. Defaults to 'single'.
        tags: Optional list of tag strings to associate with the list.
        description: Optional free-text description for the new list.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The MailingList object that was created on the server, including its
        assigned id and uuid.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        ValueError: If list_name is empty, or if list_type or optin is not one of
            its accepted values.
        ValidationError: If the server returns an empty or invalid JSON response.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.

    Examples:
        >>> import listmonk
        >>> new_list = listmonk.create_list('Newsletter', list_type='public', optin='double')
        >>> new_list.id
        7
    """
    global core_headers

    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)
    list_name = (list_name or '').strip()

    if not list_name:
        raise ValueError('List name is required')

    if list_type not in ['public', 'private']:
        raise ValueError("list_type must be either 'public' or 'private'")

    if optin not in ['single', 'double']:
        raise ValueError("optin must be either 'single' or 'double'")

    payload: dict[str, Any] = {
        'name': list_name,
        'type': list_type,
        'optin': optin,
    }

    if tags is not None:
        payload['tags'] = tags

    if description is not None:
        payload['description'] = description

    url = f'{url_base}{urls.lists}'

    resp = httpx2.post(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=payload,
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    list_data = raw_data['data']

    return models.MailingList(**list_data)


# endregion


# region def delete_list(list_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool


def delete_list(list_id: int, timeout_config: Optional[httpx2.Timeout] = None) -> bool:
    """
    Delete a mailing list by its ID.

    The list's existence is checked first via list_by_id, which raises if the
    list does not exist.

    Args:
        list_id: The numeric ID of the list to delete. Must be a truthy value
            (0 or None is rejected).
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        True if the server reports the list was deleted, False if the server
        response does not confirm deletion.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        ValueError: If list_id is missing or falsy.
        ValidationError: If the server returns an empty or invalid JSON response.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status,
            including when the existence check finds no list with the given ID.
    """

    global core_headers

    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    if not list_id:
        raise ValueError('List ID is required to delete a list.')

    # Pre-flight existence check: list_by_id raises if the list doesn't exist.
    list_by_id(list_id, timeout_config)

    url = f'{url_base}{urls.lst}'
    url = url.format(list_id=list_id)

    resp = httpx2.delete(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)

    # Expecting {'data': True} on success
    return raw_data.get('data', False)


# endregion


# region def update_list(list_id: int, ...) -> models.MailingList


def update_list(
    list_id: int,
    list_name: Optional[str] = None,
    list_type: Optional[str] = None,
    status: Optional[str] = None,
    optin: Optional[str] = None,
    tags: Optional[list[str]] = None,
    description: Optional[str] = None,
    timeout_config: Optional[httpx2.Timeout] = None,
) -> models.MailingList:
    """
    Update an existing mailing list on the server.

    Only the parameters you pass (that are not None) are included in the update
    payload, so omitted fields are left unchanged.

    Args:
        list_id: The numeric ID of the list to update. Required.
        list_name: Optional new name for the list (stripped of surrounding whitespace).
        list_type: Optional new visibility. One of 'public' or 'private'.
        status: Optional new status. One of 'active' or 'archived'.
        optin: Optional new opt-in mode. One of 'single' or 'double'.
        tags: Optional new list of tag strings for the list.
        description: Optional new description for the list.
        timeout_config: Optional per-request timeout; defaults to 10 seconds.

    Returns:
        The updated MailingList object as returned by the server.

    Raises:
        OperationNotAllowedError: If the base URL is not set or you are not logged in.
        ValueError: If list_id is missing, or if list_type, status, or optin is not
            one of its accepted values.
        ValidationError: If the server returns an empty or invalid JSON response.
        httpx2.HTTPStatusError: If the server responds with a 4xx or 5xx status.
    """
    global core_headers

    validate_state(url=True)
    timeout_config = timeout_config or httpx2.Timeout(timeout=10)

    if not list_id:
        raise ValueError('List ID is required')

    if list_type not in [None, 'public', 'private']:
        raise ValueError("list_type must be either 'public' or 'private'")

    if status not in [None, 'active', 'archived']:
        raise ValueError("status must be either 'active' or 'archived'")

    if optin not in [None, 'single', 'double']:
        raise ValueError("optin must be either 'single' or 'double'")

    payload: dict[str, Any] = {}

    if list_name is not None:
        list_name = (list_name or '').strip()
        payload['name'] = list_name

    if list_type is not None:
        payload['type'] = list_type

    if optin is not None:
        payload['optin'] = optin

    if status is not None:
        payload['status'] = status

    if tags is not None:
        payload['tags'] = tags

    if description is not None:
        payload['description'] = description

    url = f'{url_base}{urls.lst}'
    url = url.format(list_id=list_id)

    resp = httpx2.put(
        url,
        auth=httpx2.BasicAuth(username or '', password or ''),
        json=payload,
        headers=core_headers,
        follow_redirects=True,
        timeout=timeout_config,
    )
    raw_data = _validate_and_parse_json_response(resp)
    list_data = raw_data['data']

    return models.MailingList(**list_data)


# endregion
