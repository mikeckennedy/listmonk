## models.CampaignStatuses


The lifecycle status of a campaign.


Usage

``` python
models.CampaignStatuses()
```


## Attributes


`draft`  
Created but not queued; safe to edit.

`scheduled`  
Will start automatically at the campaign's send_at time.

`running`  
Actively sending to the target lists.

`paused`  
Sending has been halted and can be resumed.

`cancelled`  
Sending was stopped and will not resume.

`finished`  
All messages have been sent.


## Examples

``` python
>>> import listmonk
>>> from listmonk.models import CampaignStatuses
>>> listmonk.set_campaign_status(7, CampaignStatuses.running).status
'running'
```


## Attributes

| Name | Description |
|----|----|
| [cancelled](#cancelled) | The lifecycle status of a campaign. |
| [draft](#draft) | The lifecycle status of a campaign. |
| [finished](#finished) | The lifecycle status of a campaign. |
| [paused](#paused) | The lifecycle status of a campaign. |
| [running](#running) | The lifecycle status of a campaign. |
| [scheduled](#scheduled) | The lifecycle status of a campaign. |

------------------------------------------------------------------------


#### cancelled


The lifecycle status of a campaign.


`cancelled=``"cancelled"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status


------------------------------------------------------------------------


#### draft


The lifecycle status of a campaign.


`draft=``"draft"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status


------------------------------------------------------------------------


#### finished


The lifecycle status of a campaign.


`finished=``"finished"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status


------------------------------------------------------------------------


#### paused


The lifecycle status of a campaign.


`paused=``"paused"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status


------------------------------------------------------------------------


#### running


The lifecycle status of a campaign.


`running=``"running"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status


------------------------------------------------------------------------


#### scheduled


The lifecycle status of a campaign.


`scheduled=``"scheduled"`


Attributes: draft: Created but not queued; safe to edit. scheduled: Will start automatically at the campaign's send_at time. running: Actively sending to the target lists. paused: Sending has been halted and can be resumed. cancelled: Sending was stopped and will not resume. finished: All messages have been sent.

##### Examples

\`\`\`python \>\>\> import listmonk \>\>\> from listmonk.models import CampaignStatuses \>\>\> listmonk.set_campaign_status(7, CampaignStatuses.running).status
