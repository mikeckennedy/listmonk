## models.SubscriberStatus


A breakdown of subscriber counts by subscription status for a mailing list.


Usage

``` python
models.SubscriberStatus()
```


## Attributes


`unconfirmed_count: Optional[int]`  
The number of subscriptions still awaiting double opt-in confirmation (read from the API's `unconfirmed` field).


## Examples

``` python
>>> import listmonk
>>> lst = listmonk.list_by_id(7)
>>> lst.subscriber_statuses.unconfirmed_count
5
```
