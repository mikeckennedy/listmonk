import json
from pathlib import Path

import listmonk

file = Path(__file__).parent / 'settings.json'

settings = {}
if file.exists():
    settings = json.loads(file.read_text())

url = settings.get('base_url') or input("Enter the base URL for your instance: ")
user = settings.get('username') or input("Enter the username for Umami: ")
password = settings.get('password') or input("Enter the password for Umami: ")
test_list_id = settings.get('test_list_id') or input("Enter the ID for a test list with subscribers: ")

listmonk.set_url_base(url)
print(f'Base url: {listmonk.get_base_url()}')

print(f"Logged in? {listmonk.login(user, password)}")
print(f"API Healthy?: {listmonk.is_healthy()}")
print(f"Verify login: {listmonk.verify_login()}")
print()

lists = listmonk.lists()
for lst in lists:
    print(f'{lst.name} list: {lst}')

lst = listmonk.list_by_id(6)
print(f'List by ID: {lst}')

print()
subscribers = listmonk.subscribers(list_id=test_list_id)
print(f'{len(subscribers):,} subscribers returned')

# id=208495 created_at=datetime.datetime(2024, 1, 19, 20, 29, 8, 477242, tzinfo=TzInfo(UTC))
# updated_at=datetime.datetime(2024, 1, 19, 20, 29, 8, 477242, tzinfo=TzInfo(UTC))
# uuid='9a6b65de-c73d-4b9d-8e88-9bdd9439aff2' email='testuser_mkennedy@mkennedy.domain'
# name='Michael Test Listmonk' attribs={'email': 'testuser_mkennedy@mkennedy.domain', 'first_name': '',
# 'groups': ['friendsofthetalkpython'], 'last_changed': '', 'last_name': '',
# 'location': {'country_code': '', 'region': '', 'timezone': ''},
# 'optin': {'confirm_ip_address': '1.2.3.4', 'confirm_time': '2023-01-19 15:31:42',
# 'latitude': '', 'longitude': '', 'optin_ip_address': '', 'optin_time': '2022-04-26 15:31:42'}, 'rating': 1}

subscriber = listmonk.subscriber_by_email('testuser_mkennedy@mkennedy.domain')
print(f'Subscriber by email: {subscriber}')

subscriber = listmonk.subscriber_by_id(subscriber.id)
print(f'Subscriber by id: {subscriber}')

subscriber = listmonk.subscriber_by_uuid(subscriber.uuid)
print(f'Subscriber by uuid: {subscriber}')

deletable_email = 'deletable_user@mkennedy.com'

if listmonk.subscriber_by_email(deletable_email):
    print(f"Deletable subscriber already exists: {deletable_email}, deleting them!")
    listmonk.delete_subscriber(deletable_email)

custom_data = {
    'email': deletable_email,
    'rating': 1,
}

new_subscriber = listmonk.create_subscriber(deletable_email, 'Deletable Mkennedy',
                                            [test_list_id], pre_confirm=True, attribs=custom_data)
print(f'Created subscriber: {new_subscriber}')

new_subscriber.name = 'Mr. ' + new_subscriber.name.upper()
new_subscriber.attribs['rating'] = 7

updated_subscriber = listmonk.update_subscriber(new_subscriber, {4, 6}, {5})
print(f'Updated subscriber: {updated_subscriber}')
# success = listmonk.delete_subscriber(overriding_subscriber_id=new_subscriber.id)
# print(f"Deleted {deletable_email} successfully? {success}")


updated_subscriber.attribs['subscription_note'] = \
    "They asked to be unsubscribed so we disabled their account, but no block-listing yet."

disabled_subscriber = listmonk.disable_subscriber(updated_subscriber)
print("Disabled: ", disabled_subscriber)

disabled_subscriber.attribs['blocklist_note'] = \
    "They needed to be blocked!"

listmonk.block_subscriber(disabled_subscriber)

re_enabled_subscriber = listmonk.enable_subscriber(disabled_subscriber)
print("Re-enabled: ", re_enabled_subscriber)

listmonk.delete_subscriber(deletable_email)

to_email = 'SUBSCRIBER_EMAIL_ON_YOUR_LIST'
from_email = 'APPROVED_OUTBOUND_EMAIL_ON_DOMAIN'
template_id = 3  # Default from listmonk setup.
template_data = {'order_id': 1772, 'shipping_date': 'Next week'}
if to_email != 'SUBSCRIBER_EMAIL_ON_YOUR_LIST':
    status = listmonk.send_transactional_email(to_email, template_id, from_email=from_email,
                                               template_data=template_data, content_type='html')
    print(f"Result of sending a tx email: {status}.")
else:
    print("Set email values to send transactional emails.")
