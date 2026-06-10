import json
from pathlib import Path

import listmonk
from listmonk.models import MailingList, Subscriber

file: Path = Path(__file__).parent / 'settings.json'

settings = {}
if file.exists():
    settings = json.loads(file.read_text())

url: str = settings.get('base_url', '').strip('/') or input('Enter the base URL for your instance: ')
user: str = settings.get('username') or input('Enter the username for Listmonk: ')
password: str = settings.get('password') or input('Enter the password for Listmonk: ')
test_list_id: int = int(settings.get('test_list_id') or input('Enter the ID for a test list with subscribers: '))

listmonk.set_url_base(url)
print(f'Base url: {listmonk.get_base_url()}', flush=True)

if not listmonk.login(user, password):
    raise SystemExit('Login failed: check your username/password and base URL.')
print('Logged in successfully', flush=True)
print(f'API Healthy?: {listmonk.is_healthy()}', flush=True)
print(f'Verify login: {listmonk.verify_login()}', flush=True)
print()

lists: list[MailingList] = listmonk.lists()
for lst in lists:
    print(f'{lst.name} list: {lst}', flush=True)

the_list = listmonk.list_by_id(test_list_id)
print(f'List by ID: {the_list}')

print()
subscribers: list[Subscriber] = listmonk.subscribers(list_id=test_list_id)
print(f'{len(subscribers):,} subscribers returned', flush=True)

# id=208495 created_at=datetime.datetime(2024, 1, 19, 20, 29, 8, 477242, tzinfo=TzInfo(UTC))
# updated_at=datetime.datetime(2024, 1, 19, 20, 29, 8, 477242, tzinfo=TzInfo(UTC))
# uuid='9a6b65de-c73d-4b9d-8e88-9bdd9439aff2' email='testuser_mkennedy@mkennedy.domain'
# name='Michael Test Listmonk' attribs={'email': 'testuser_mkennedy@mkennedy.domain', 'first_name': '',
# 'groups': ['friendsofthetalkpython'], 'last_changed': '', 'last_name': '',
# 'location': {'country_code': '', 'region': '', 'timezone': ''},
# 'optin': {'confirm_ip_address': '1.2.3.4', 'confirm_time': '2023-01-19 15:31:42',
# 'latitude': '', 'longitude': '', 'optin_ip_address': '', 'optin_time': '2022-04-26 15:31:42'}, 'rating': 1}

custom_data = {
    'email': 'newemail@some.domain',
    'rating': 1,
}

email = 'deletable_user@mkennedy.domain'
if subscriber := listmonk.subscriber_by_email(email):
    listmonk.delete_subscriber(subscriber.email)

subscriber = listmonk.create_subscriber(
    email, 'Deletable Mkennedy', {test_list_id}, pre_confirm=True, attribs=custom_data
)
print(f'Created subscriber: {subscriber}', flush=True)

subscriber = listmonk.subscriber_by_email(email)
print(f'Subscriber by email: {subscriber}', flush=True)

subscriber = listmonk.subscriber_by_id(subscriber.id)  # type: ignore
print(f'Subscriber by id: {subscriber}', flush=True)

subscriber = listmonk.subscriber_by_uuid(subscriber.uuid)  # type: ignore
print(f'Subscriber by uuid: {subscriber}', flush=True)

subscriber.name = 'Mr. ' + subscriber.name.upper()  # type: ignore
subscriber.attribs['rating'] = 7  # type: ignore

query = f"subscribers.email = '{email}'"
print('Searching for user with query: ', query, flush=True)
sub2 = listmonk.subscribers(query)
print(f'Found {len(sub2):,} users with query.', flush=True)
print(f'Found {sub2[0].name} with email {sub2[0].email}', flush=True)


# TODO: Choose list IDs from your instance (can be seen in the UI or from the listing above)
to_add = {the_list.id}  # Add all the lists here: {1, 7, 11},  # type: ignore
remove_from = set()  # Same as above
updated_subscriber = listmonk.update_subscriber(subscriber, to_add, remove_from)
print(f'Updated subscriber: {updated_subscriber}', flush=True)

if subscriber is not None and the_list is not None:
    print(f'Subscriber confirmed?: {listmonk.confirm_optin(subscriber.uuid, the_list.uuid)}', flush=True)

if updated_subscriber:
    updated_subscriber.attribs['subscription_note'] = (
        'They asked to be unsubscribed so we disabled their account, but no block-listing yet.'
    )

    disabled_subscriber = listmonk.disable_subscriber(updated_subscriber)
    print('Disabled: ', disabled_subscriber, flush=True)

    if disabled_subscriber is not None:
        disabled_subscriber.attribs['blocklist_note'] = 'They needed to be blocked!'
        listmonk.block_subscriber(disabled_subscriber)

        re_enabled_subscriber = listmonk.enable_subscriber(disabled_subscriber)
        print('Re-enabled: ', re_enabled_subscriber, flush=True)

# Create, rename, bulk-add to, then delete a temporary list.
new_list = listmonk.create_list('Example Temp List', list_type='private', optin='single')
print(f'Created list: {new_list.name} (id {new_list.id})', flush=True)

renamed_list = listmonk.update_list(new_list.id, list_name='Renamed Temp List')
print(f'Renamed list: {renamed_list.name}', flush=True)

if subscriber:
    added = listmonk.add_subscribers_to_lists([subscriber.id], [new_list.id])
    print(f'Bulk-added subscriber to list: {added}', flush=True)

print(f'Deleted list: {listmonk.delete_list(new_list.id)}', flush=True)

if subscriber:
    listmonk.delete_subscriber(subscriber.email)

# Campaigns: list, create, fetch, preview, update, delete.
campaigns = listmonk.campaigns()
print(f'{len(campaigns):,} campaigns on the server.', flush=True)

campaign = listmonk.create_campaign(
    name='Example Temp Campaign',
    subject='Hello from the example client',
    list_ids={test_list_id},
    content_type='html',
    body='<p>Hi there!</p>',
)
print(f'Created campaign: {campaign.name} (id {campaign.id})', flush=True)

campaign_preview = listmonk.campaign_preview_by_id(campaign.id)
print(f'Campaign preview is {len(campaign_preview.preview or "")} characters of HTML.', flush=True)

fetched_campaign = listmonk.campaign_by_id(campaign.id)
if fetched_campaign:
    fetched_campaign.subject = 'An even better subject'
    updated_campaign = listmonk.update_campaign(fetched_campaign)
    print(f'Updated campaign subject: {updated_campaign.subject if updated_campaign else None}', flush=True)

print(f'Deleted campaign: {listmonk.delete_campaign(campaign.id)}', flush=True)

# Templates: list, create, fetch, preview, update, delete.
templates = listmonk.templates()
print(f'{len(templates):,} templates on the server.', flush=True)

tmpl = listmonk.create_template(
    name='Example Temp Template',
    body='<header>Example</header> {{ template "content" . }} <footer>Bye!</footer>',
    type='campaign',
)
print(f'Created template: {tmpl.name} (id {tmpl.id})', flush=True)

template_preview = listmonk.template_preview_by_id(tmpl.id)
print(f'Template preview is {len(template_preview.preview or "")} characters of HTML.', flush=True)

fetched_template = listmonk.template_by_id(tmpl.id)
if fetched_template:
    fetched_template.name = 'Renamed Temp Template'
    listmonk.update_template(fetched_template)

# To make a template the default for its type: listmonk.set_default_template(tmpl.id)
print(f'Deleted template: {listmonk.delete_template(tmpl.id)}', flush=True)

to_email = 'SUBSCRIBER_EMAIL_ON_YOUR_LIST'
from_email = 'APPROVED_OUTBOUND_EMAIL_ON_DOMAIN'  # Optional; leave as is to use the server's default sender.
template_id = 3  # *Transactional* template ID from your listmonk instance.
template_data = {'order_id': 1772, 'shipping_date': 'Next week'}
altbody = 'Your order 1772 ships next week.'
if to_email != 'SUBSCRIBER_EMAIL_ON_YOUR_LIST':
    # Only pass from_email once you've set a real address; omitting it uses the server default.
    kwargs = {} if from_email == 'APPROVED_OUTBOUND_EMAIL_ON_DOMAIN' else {'from_email': from_email}
    status = listmonk.send_transactional_email(
        to_email,
        template_id,
        template_data=template_data,
        content_type='html',
        altbody=altbody,
        # attachments=[Path('/path/to/invoice.pdf')],  # Optional file attachments
        **kwargs,
    )
    print(f'Result of sending a tx email: {status}.', flush=True)
else:
    print('Set email values to send transactional emails.', flush=True)
