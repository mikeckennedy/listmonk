## models.MailingList


A mailing list on the Listmonk instance.


Usage

``` python
models.MailingList()
```


## Attributes


`id: int`  
The numeric list ID assigned by Listmonk.

`created_at: datetime.datetime`  
When the list was created.

`updated_at: Optional[datetime.datetime]`  
When the list was last modified, if ever.

`uuid: str`  
The globally unique identifier for the list.

`name: Optional[str]`  
The human-readable list name.

`type: Optional[str]`  
The list visibility, typically `public` or `private`.

`optin: Optional[str]`  
The opt-in mode, either `single` or `double`.

`tags: list[str]`  
Arbitrary labels attached to the list.

`description: Optional[str]`  
A free-text description of the list.

`subscriber_count: Optional[int]`  
The total number of subscribers on the list.

`subscriber_statuses: Optional[SubscriberStatus]`  
A breakdown of subscriber counts by subscription status.
