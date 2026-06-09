## models.Subscriber


A subscriber (contact) on the Listmonk instance.


Usage

``` python
models.Subscriber()
```


## Attributes


`id: int`  
The numeric subscriber ID assigned by Listmonk.

`email: str`  
The subscriber's email address (their primary identifier).

`name: Optional[str]`  
The subscriber's display name, if provided.

`created_at: datetime.datetime`  
When the subscriber was created.

`updated_at: Optional[datetime.datetime]`  
When the subscriber was last modified, if ever.

`uuid: Optional[str]`  
The globally unique identifier for the subscriber.

`lists: list[dict[str, Any]]`  
The lists this subscriber belongs to, each as a dict describing the membership (list id, subscription status, and so on).

`attribs: dict[str, Any]`  
Arbitrary custom attributes stored against the subscriber.

`status: Optional[str]`  
The subscriber's global status, e.g. [enabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.enabled), [disabled](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.disabled), or [blocklisted](models.SubscriberStatuses.md#listmonk.models.SubscriberStatuses.blocklisted).
