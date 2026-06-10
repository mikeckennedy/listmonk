## send_transactional_email()


Send a transactional email through Listmonk to a single recipient.


Usage

``` python
send_transactional_email(
    subscriber_email,
    template_id,
    from_email=None,
    template_data=None,
    messenger_channel="email",
    content_type="markdown",
    altbody=None,
    attachments=None,
    email_headers=None,
    timeout_config=None
)
```


The recipient must already be a subscriber on at least one list. Delivery errors may surface in the logs section of your Listmonk dashboard rather than as exceptions here. The subscriber_email is lowercased and stripped before sending.


## Parameters


`subscriber_email: str`  
The recipient's email address. Required; they must be a subscriber of some list on your server.

`template_id: int`  
The ID of the template to render. Must be a 'tx' (transactional) template, not a campaign template.

`from_email: Optional[str] = None`  
The From address. Omit to use the default address at your sending provider.

`template_data: Optional[dict[str, Any]] = None`  
Merge parameters available in the template as {{ .Tx.Data.\* }}. Defaults to an empty dict.

`messenger_channel: str = ``"email"`  
The delivery channel. Defaults to 'email'; use another configured channel (e.g. SMS) if available.

`content_type: str = ``"markdown"`  
The body format: 'html', 'markdown', or 'plain'. Defaults to 'markdown'.

`altbody: Optional[str] = None`  
Optional alternate plain-text body for multipart HTML emails.

`attachments: Optional[list[Path]] = None`  
Optional list of pathlib.Path objects pointing to files to attach. Each path must exist and be a file.

`email_headers: Optional[list[dict[str, Optional[str]]]] = None`  
Optional list of custom headers, each a single-entry dict, e.g. \[{'X-Custom': 'value'}\].

`timeout_config: Optional[httpx2.Timeout] = None`  
Optional per-request timeout; defaults to 10 seconds.


## Returns


`bool`  
True if the server accepted the send, False otherwise.


## Raises


`ValueError`  
If subscriber_email is empty.

`ListmonkFileNotFoundError`  
If any attachment path does not exist or is not a file.

`OperationNotAllowedError`  
If the base URL has not been set or you have not logged in.

`httpx2.HTTPStatusError`  
If the server responds with a 4xx or 5xx status.

`ValidationError`  
If the response is empty or is not valid JSON.


## Examples

``` python
>>> import listmonk
>>> listmonk.send_transactional_email(
...     subscriber_email='person@example.com',
...     template_id=3,
...     template_data={'name': 'Sam'},
... )
True
```
