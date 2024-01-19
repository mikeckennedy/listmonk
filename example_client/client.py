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
print(subscribers[0])
# id=208494 created_at=datetime.datetime(2024, 1, 18, 8, 19, 23, 159797, tzinfo=TzInfo(UTC)) updated_
# at=datetime.datetime(2024, 1, 18, 8, 19, 23, 159797,
# tzinfo=TzInfo(UTC)) uuid='383621d2-34bc-4e41-beda-7bf5e3d4f04f' email='jduculan@yahoo.com' name='Friend'
# attribs={'email': 'jduculan@yahoo.com',
# 'first_name': '', 'groups': ['friendsofthetalkpython'], 'last_changed': '', 'last_name': '', 'location':
# {'country_code': '', 'region': '', 'timezone': ''},
# 'optin': {'confirm_ip_address': '162.243.162.68', 'confirm_time': '2022-04-26 15:31:42', 'latitude': '',
# 'longitude': '', 'optin_ip_address': '', 'optin_time':
# '2022-04-26 15:31:42'}, 'rating': 1}

subscriber = listmonk.subscriber_by_email('jduculan@yahoo.com')
print(f'Subscriber by email: {subscriber}')

subscriber = listmonk.subscriber_by_id(subscriber.id)
print(f'Subscriber by id: {subscriber}')

subscriber = listmonk.subscriber_by_uuid(subscriber.uuid)
print(f'Subscriber by uuid: {subscriber}')
