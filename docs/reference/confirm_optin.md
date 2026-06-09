## confirm_optin()


For opt-in situations, subscribers are added as unconfirmed first. This method will opt them in


Usage

``` python
confirm_optin(
    subscriber_uuid,
    list_uuid,
    timeout_config=None,
)
```


via the API. You should only do this when they are actually opting in. If you have your own opt-in form, but it's via your code, then this makes sense.


## Parameters


`subscriber_uuid: Optional[str]`  
The Subscriber.uuid value for the subscriber.

`list_uuid: Optional[str]`  
The MailingList.uuid value for the list.

`timeout_config: Optional[httpx.Timeout] = None`  
Optional timeout configuration for the request. Default is 10 seconds.


## Returns


`bool`  
True if they were successfully opted in.
