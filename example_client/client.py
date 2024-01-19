import json
from pathlib import Path

import listmonk

file = Path(__file__).parent / 'settings.json'

settings = {}
if file.exists():
    settings = json.loads(file.read_text())

print(listmonk.user_agent)

url = settings.get('base_url') or input("Enter the base URL for your instance: ")
user = settings.get('username') or input("Enter the username for Umami: ")
password = settings.get('password') or input("Enter the password for ")

listmonk.set_url_base(url)

print(f"Logged in? {listmonk.login(user, password)}")
print(f"API Healthy?: {listmonk.is_healthy()}")
print(f"Verify login: {listmonk.verify_login()}")
print()

lists = listmonk.lists()
for lst in lists:
    print(lst)

lst = listmonk.list_by_id(6)
print(lst)

subscribers = listmonk.subscribers()
print(f'{len(subscribers):,} subscribers returned')
print(subscribers[0])
# websites = umami.websites()
# print(f"Found {len(websites):,} websites.")
# print("First website in list:")
# print(websites[0])
# print()
#
# if test_domain := settings.get('test_domain'):
#
#     test_site = [w for w in websites if w.domain == test_domain][0]
#     print(f"Using {test_domain} for testing events.")
#
#     event_resp = umami.new_event(
#         website_id=test_site.id,
#         event_name='Umami-Test-Event3',
#         title='Umami-Test-Event3',
#         hostname=test_site.domain,
#         url='/users/actions',
#         custom_data={'client': 'umami-tester-v1'},
#         referrer='https://talkpython.fm')
#
#     print(f"Created new event: {event_resp}")
# else:
#     print("No test domain, skipping event creation.")
