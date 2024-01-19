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


