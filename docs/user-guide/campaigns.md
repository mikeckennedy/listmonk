# Campaigns

A campaign is one message aimed at one or more lists: the newsletter, the launch announcement, the "we changed our pricing" email. Unlike a transactional send it has a life cycle, and the most important thing to know is that creating a campaign does not send it. Sending is a separate, deliberate step, with a test send in between so you can read the result in your own inbox first.


# The life cycle

A campaign is born a [draft](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.draft). From there it can become [scheduled](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.scheduled) (it will start itself at `send_at`) or [running](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.running) (it is sending now). A running campaign can be [paused](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.paused) and resumed, or [cancelled](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.cancelled) for good. When every message has gone out it is [finished](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.finished). Those six values are the [`CampaignStatuses`](../reference/models.CampaignStatuses.md) enum, and Listmonk only permits certain moves between them: draft to scheduled or running, scheduled back to draft, running to paused or cancelled, paused to running. Ask for anything else and the server answers 400.


# Creating one

``` python
from datetime import datetime, timedelta

campaign = listmonk.create_campaign(
    name='June newsletter',
    subject='What shipped in June',
    list_ids={1, 2},
    content_type='markdown',
    body='# Big news\n\nHello there!',
    alt_body='Big news. Hello there!',
    tags=['newsletter'],
    send_at=datetime.now() + timedelta(hours=1),   # optional: schedule it
)
print(campaign.id, campaign.status)  # 42 draft
```

[`create_campaign()`](../reference/create_campaign.md) requires a name and a subject; everything else has a default. `list_ids` defaults to `{1}`, Listmonk's default list, so set it. `content_type` is `richtext`, `html`, `markdown`, or `plain`. `template_id` left as `None` means the server's default campaign template. `from_email` falls back to the instance setting and is sent exactly as you write it, so `Newsletter <news@example.com>` keeps its display name. Custom `headers` are a list of single-entry dicts.

`send_at` takes a `datetime`; a naive one is treated as local time when it is serialised. Note that setting `send_at` does not by itself schedule the campaign. It is still a draft until you move it to [scheduled](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.scheduled) (see below), at which point Listmonk starts it at that time.


# Attachments

Attaching a file to a campaign is a two-step dance: upload it to Listmonk's media library, then reference its ID.

``` python
from pathlib import Path

media = listmonk.upload_media(Path('/reports/june-chart.png'))
# or from bytes: listmonk.upload_media(png_bytes, filename='june-chart.png')

campaign = listmonk.create_campaign('June', 'Our June numbers', media_ids=[media.id])
```

[`upload_media()`](../reference/upload_media.md) returns a [`Media`](../reference/models.Media.md) model whose `id` goes into `media_ids`. A default Listmonk install only accepts image extensions in the media library; widen Settings, Media, Upload extensions on the server for PDFs and the like. The client does not wrap the endpoints for listing or deleting media, so clean up through the admin UI.


# Changing a draft

``` python
campaign = listmonk.campaign_by_id(42)
campaign.subject = 'What shipped in June (and one thing that did not)'
campaign.lists = [1, 2, 5]
campaign = listmonk.update_campaign(campaign)
```

[`update_campaign()`](../reference/update_campaign.md) sends the whole campaign back and returns the server's fresh copy. Three things to know:

- Attachments are replaced as a set on every update. With `media_ids` left as `None` the client re-sends the campaign's current attachments so nothing is lost; `media_ids=[]` clears them; a new list swaps them.
- A `send_at` that is already in the past is dropped (sent as `null`) so a stale schedule does not fail the update, and Listmonk then moves a [scheduled](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.scheduled) campaign back to [draft](../reference/models.CampaignStatuses.md#listmonk.models.CampaignStatuses.draft).
- It cannot change the status. Listmonk ignores `status` on this endpoint; use the status calls below.


# Preview

``` python
html = listmonk.campaign_preview_by_id(42).preview
```

[`campaign_preview_by_id()`](../reference/campaign_preview_by_id.md) returns the campaign rendered through its template as an HTML string, the same thing the admin's preview pane shows. Handy for a last look, or for dropping into a test that checks the merge fields came out right.


# Test before you send

``` python
listmonk.test_campaign(42, ['you@example.com', 'editor@example.com'])  # True
```

[`test_campaign()`](../reference/test_campaign.md) sends the campaign to the addresses you name and leaves the campaign untouched: still a draft, statistics unchanged. The test copy carries the subject, body, alternate body, custom headers, template, and From address as saved on the server, so what you read is what the list will get.

Every test address must already exist as a subscriber. Listmonk does not create them, and when none of the addresses are known it rejects the request with HTTP 400 ("No known subscribers to test."), which the client raises as `httpx2.HTTPStatusError`. Keep yourself on a private "staff" list and this is never a problem.


# Send, pause, cancel

``` python
from listmonk.models import CampaignStatuses

listmonk.start_campaign(42)     # draft -> running
listmonk.pause_campaign(42)     # running -> paused
listmonk.start_campaign(42)     # paused -> running again
listmonk.cancel_campaign(42)    # stop for good

listmonk.set_campaign_status(42, CampaignStatuses.scheduled)  # draft -> scheduled, fires at send_at
```

[`start_campaign()`](../reference/start_campaign.md), [`pause_campaign()`](../reference/pause_campaign.md), and [`cancel_campaign()`](../reference/cancel_campaign.md) are thin wrappers over [`set_campaign_status()`](../reference/set_campaign_status.md), which talks to Listmonk's dedicated status endpoint. Reach for [set_campaign_status()](../reference/set_campaign_status.md#listmonk.set_campaign_status) directly for the other members of the enum, and always pass the enum rather than a bare string: an unrecognised status reaches Postgres and comes back as an opaque HTTP 500. All four return the updated [`Campaign`](../reference/models.Campaign.md), or `None` if no campaign has that ID, and raise `httpx2.HTTPStatusError` for a transition the server refuses.


# Reading progress

The [`Campaign`](../reference/models.Campaign.md) model carries `status`, `to_send`, `sent`, `views`, `clicks`, and `started_at`, so a dashboard can poll [`campaign_by_id()`](../reference/campaign_by_id.md) while a send runs. [`campaigns()`](../reference/campaigns.md) returns every campaign on the instance in one request. Deeper analytics (opens over time, link-level clicks) are not wrapped by this client; use the admin or the Listmonk API directly for those.


# Deleting

``` python
listmonk.delete_campaign(42)  # True, or False if there was no such campaign
```

[`delete_campaign()`](../reference/delete_campaign.md) looks the campaign up first and returns `False` without issuing a delete when it does not exist.
