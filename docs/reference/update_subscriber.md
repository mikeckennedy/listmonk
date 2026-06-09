## update_subscriber()


Update many aspects of a subscriber, from their email addresses and names, to custom attribute data, and


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


from adding them to and removing them from lists. You can enable, disable, and block them here. But if that is all you want tod o there are functions dedicated to that which are simpler.


## Parameters


`subscriber: Optional[models.Subscriber]`  
The full subscriber object to update (with changed fields and values)

`add_to_lists: Optional[set[int]] = None`  
Any list to add to this subscriber to.

`remove_from_lists: Optional[set[int]] = None`  
Any list to remove from this subscriber.

`status: SubscriberStatuses = SubscriberStatuses.enabled`    
The status of the subscriber: enabled, disabled, blacklisted from SubscriberStatuses.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`Optional[models.Subscriber]`  
The updated view of the subscriber object from the server.
