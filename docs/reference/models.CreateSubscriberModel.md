## models.CreateSubscriberModel


The payload used to create a new subscriber.


Usage

``` python
models.CreateSubscriberModel()
```


## Attributes


`email: str`  
The email address for the new subscriber.

`name: Optional[str]`  
The subscriber's display name, if any.

`status: str`  
The initial global status, e.g. [enabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.enabled).

`lists: list[int]`  
The IDs of the lists to subscribe this person to.

`preconfirm_subscriptions: bool`  
When `True`, mark the new subscriptions as confirmed immediately (skipping double opt-in confirmation emails).

`attribs: dict[str, Any]`  
Arbitrary custom attributes to store against the subscriber.
