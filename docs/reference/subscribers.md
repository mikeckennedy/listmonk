## subscribers()


Get a list of subscribers matching the criteria provided. If none, then all subscribers are returned.


Usage

``` python
subscribers(
    query_text=None,
    list_id=None,
    timeout_config=None,
)
```


## Parameters


`query_text: Optional[str] = None`  
Custom query text such as "subscribers.attribs-\>\>'city' = 'Portland'". See the full documentation at https://listmonk.app/docs/querying-and-segmentation/

`list_id: Optional[int] = None`  
Pass a list ID and get the subscribers, matching the query, from that list.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`list[models.Subscriber]`  
A list of subscribers matching the criteria provided. If none, then all subscribers are returned.
