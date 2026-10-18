## send_transactional_email()


Send a transactional email through Listmonk to one or more recipients.


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
    timeout_config=None,
    subscriber_mode=None
)
```


By default the recipient must already be a subscriber on at least one list (see subscriber_mode to relax this). Delivery errors may surface in the logs section of your Listmonk dashboard rather than as exceptions here. Recipient addresses are lowercased and stripped before sending.


## Parameters


`subscriber_email: Union[str, list[str]]`  
The recipient's email address, or a list of addresses to send to several recipients in one call. By default each recipient must already be a subscriber of some list on your server; see subscriber_mode to relax that. Addresses are lowercased and stripped.

`template_id: int`  
The ID of the template to render. Required. Must be a 'tx' (transactional) template, not a campaign template.

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

`subscriber_mode: Optional[Literal[``"default", `<span class="st">`"fallback"``, ``"external"``]]`</span>` = None`  
How the server resolves each recipient, on Listmonk servers that support it. One of 'default', 'fallback', or 'external'. Omit it (None) and the field is left off the request entirely, so the server keeps its own default behavior of requiring a subscriber. 'fallback' looks the recipient up but sends anyway if not found. 'external' skips the lookup, so you can send to non-subscribers. In 'fallback' and 'external' modes, subscriber fields other than the email are unavailable in templates; use {{ .Tx.Data.\* }} instead.


## Returns


`bool`  
True if the server accepted the send, False otherwise.


## Raises


`ValueError`  
If no recipient is given, or if a recipient list is empty or contains only blank addresses.

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

Send to several people who need not be subscribers:

``` python
>>> listmonk.send_transactional_email(
...     ['one@example.com', 'two@example.com'],
...     template_id=3,
...     subscriber_mode='external',
... )
True
```
