import json
import sys

import requests

server = sys.argv[1]
token = sys.argv[2]

url = 'https://fivesongsdaily.com/today'
api = requests.get(url)
json_response = api.json()
text = "Today's Playlist:" + '\n\r' + '\n'.join(json_response['playlist_songs'])
text += '\n\r' + 'https://www.fivesongsdaily.com'

url = f"https://{server}/api/v1/statuses"

headers = {'Authorization': f"Bearer {token}"}
params = {'status': text}

resp = requests.post(url, data=params, headers=headers)

print(json.dumps(resp.json(), indent=2))
resp.raise_for_status()
