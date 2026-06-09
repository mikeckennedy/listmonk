## create_subscriber()


Create a new subscriber on the Listmonk server.


Usage

``` python
create_subscriber(
    email,
    name=None,
    list_ids=None,
    pre_confirm=False,
    attribs=None,
    timeout_config=None
)
```


The email is lowercased and stripped and the name is stripped before the request is sent. The subscriber is always created with a global status of [enabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.enabled).


## Parameters


`email: str`  
Email address of the subscriber. Required and must be non-empty after stripping.

`name: Optional[str] = None`  
Full name (e.g. "first last") of the subscriber. Defaults to None (stored as an empty string).

`list_ids: set[int] = None`  
Set of list IDs to subscribe this person to. Defaults to None (no lists).

`pre_confirm: bool = ``False`  
When True, mark the new subscriptions as confirmed immediately so no double opt-in confirmation email is sent. Defaults to False.

`attribs: Optional[dict[str, Any]] = None`  
Custom attributes to store on the subscriber record (queryable in the subscriber UI). Defaults to None (stored as an empty dict).

`timeout_config: Optional[httpx.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`models.Subscriber`  
The newly created models.Subscriber, populated by the server with its ID, UUID, and more.


## Raises


`ValueError`  
If email is empty.

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`ValidationError`  
If the server returns an empty body or invalid JSON.

`httpx.HTTPStatusError`  
If the server rejects the request (e.g. a 4xx for a duplicate email) or returns a 5xx status.


## Examples

``` python
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
```
