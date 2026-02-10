import json
import sys

import requests

server = sys.argv[1]
token = sys.argv[2]
music_site_url = sys.argv[3]

url = f'{music_site_url}/today'
api = requests.get(url)
json_response = api.json()
text = (
    "Today's Playlist:\n\r"
    "\n\r"
    f"{json_response['playlist_theme']} - {json_response['playlist_date']}\n\r"
    "\n\r"
    f"{'\n'.join(json_response['playlist_songs'])}\n\r"
    "\n\r"
    f"{music_site_url}"
)

url = f"https://{server}/api/v1/statuses"

headers = {'Authorization': f"Bearer {token}"}
params = {'status': text}

resp = requests.post(url, data=params, headers=headers)

print(json.dumps(resp.json(), indent=2))
resp.raise_for_status()
