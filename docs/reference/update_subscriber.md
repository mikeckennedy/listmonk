## update_subscriber()


Update many aspects of a subscriber: email and name, custom attribute data, list membership, and status.


Usage

``` python
update_subscriber(
    subscriber,
    add_to_lists=None,
    remove_from_lists=None,
    status=SubscriberStatuses.enabled,
    timeout_config=None
)
```


Final list membership is computed from the subscriber's existing lists minus `remove_from_lists` plus `add_to_lists`, and the affected subscriptions are preconfirmed. You can enable, disable, or block a subscriber here, but if that is all you want to do there are dedicated, simpler functions (enable_subscriber, disable_subscriber, block_subscriber).


## Parameters


`subscriber: models.Subscriber`  
The full subscriber object to update, with the changed fields already set. Must have a valid id.

`add_to_lists: Optional[set[int]] = None`  
List IDs to add this subscriber to. Defaults to None (treated as an empty set).

`remove_from_lists: Optional[set[int]] = None`  
List IDs to remove this subscriber from. Defaults to None (treated as an empty set).

`status: SubscriberStatuses = SubscriberStatuses.enabled`    
The subscriber's status, one of SubscriberStatuses.enabled, .disabled, or .blocklisted. Defaults to SubscriberStatuses.enabled.

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The refreshed subscriber object fetched from the server after the update, or None if the subscriber

can no longer be found.


## Raises


`ValueError`  
If subscriber is None or has no id.

`OperationNotAllowedError`  
If the base URL is not set or you are not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the follow-up fetch returns an empty or invalid JSON response.
