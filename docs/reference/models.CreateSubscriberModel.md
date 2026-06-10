## models.CreateSubscriberModel


The payload used to create a new subscriber.


Usage

``` python
models.CreateSubscriberModel()
```


This is the raw request body sent to Listmonk. The higher-level [create_subscriber](create_subscriber.md#listmonk.create_subscriber) helper populates it (always sending `status='enabled'`), and [update_subscriber](update_subscriber.md#listmonk.update_subscriber) reuses it as the full PUT body when updating an existing subscriber (with the caller-supplied status).


## Attributes


`email: str`  
The email address for the new subscriber (required).

`name: Optional[str]`  
The subscriber's display name, if any.

`status: str`  
The initial global status (required), e.g. [enabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.enabled), [disabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.disabled), or [blocklisted](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.blocklisted).

`lists: list[int]`  
The IDs of the lists to subscribe this person to. Defaults to an empty list.

`preconfirm_subscriptions: bool`  
Required flag; when `True`, mark the new subscriptions as confirmed immediately (skipping double opt-in confirmation emails).

`attribs: dict[str, Any]`  
Arbitrary custom attributes to store against the subscriber. Defaults to an empty dict.
