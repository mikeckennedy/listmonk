## models.SubscriberStatuses


The global status of a subscriber on the Listmonk instance.


Usage

``` python
models.SubscriberStatuses()
```


## Attributes


`enabled`  
The subscriber is active and will receive campaigns.

`disabled`  
The subscriber is paused and will not receive campaigns.

`blocklisted`  
The subscriber has been blocked and will not receive any mail.


## Examples

``` python
>>> import listmonk
>>> from listmonk.models import SubscriberStatuses
>>> sub = listmonk.subscriber_by_email('some_user@talkpython.fm')
>>> listmonk.update_subscriber(sub, status=SubscriberStatuses.disabled).status
'disabled'
```


## Attributes

| Name | Description |
|----|----|
| [blocklisted](#blocklisted) | The global status of a subscriber on the Listmonk instance. |
| [disabled](#disabled) | The global status of a subscriber on the Listmonk instance. |
| [enabled](#enabled) | The global status of a subscriber on the Listmonk instance. |

------------------------------------------------------------------------


#### blocklisted


The global status of a subscriber on the Listmonk instance.


`blocklisted=``"blocklisted"`


Attributes: enabled: The subscriber is active and will receive campaigns. disabled: The subscriber is paused and will not receive campaigns. blocklisted: The subscriber has been blocked and will not receive any mail.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import SubscriberStatuses \>\>\> sub = listmonk.subscriber_by_email('some_user@talkpython.fm') \>\>\> listmonk.update_subscriber(sub, status=SubscriberStatuses.disabled).status


------------------------------------------------------------------------


#### disabled


The global status of a subscriber on the Listmonk instance.


`disabled=``"disabled"`


Attributes: enabled: The subscriber is active and will receive campaigns. disabled: The subscriber is paused and will not receive campaigns. blocklisted: The subscriber has been blocked and will not receive any mail.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import SubscriberStatuses \>\>\> sub = listmonk.subscriber_by_email('some_user@talkpython.fm') \>\>\> listmonk.update_subscriber(sub, status=SubscriberStatuses.disabled).status


------------------------------------------------------------------------


#### enabled


The global status of a subscriber on the Listmonk instance.


`enabled=``"enabled"`


Attributes: enabled: The subscriber is active and will receive campaigns. disabled: The subscriber is paused and will not receive campaigns. blocklisted: The subscriber has been blocked and will not receive any mail.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import SubscriberStatuses \>\>\> sub = listmonk.subscriber_by_email('some_user@talkpython.fm') \>\>\> listmonk.update_subscriber(sub, status=SubscriberStatuses.disabled).status
