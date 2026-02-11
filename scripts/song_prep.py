# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pillow",
#     "tinytag",
# ]
# ///

# uv run song_prep.py /path/to/files
# song_prep.py generates upload_YYYY-MM-DD.py

import math
import os
from os import listdir
from os.path import isfile, join
import re
import stat
import sys

from PIL import Image
from tinytag import TinyTag

template = """#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

import requests
import json
import sys

# Upload songs and capture IDs
song_ids = []
curl_host = 'https://fivesongsdaily.com'
headers = {{'Flask-Key': 'API-KEY', 'Auth-Name': 'API-USER'}}

song_objs = {songs_list}

for song in song_objs:
    files = {{
        'filepath': open(song['filepath'], 'rb'),
        'album_art': open(song['album_art'], 'rb')
    }}
    data = {{'title': song['title'], 'artist': song['artist'], 'duration': song['duration'], 'album_name': song['album_name']}}
    response = requests.post(f"{{curl_host}}/api/song/create", files=files, data=data, headers=headers)
    song_id = response.json()['song_id']
    song_ids.append(song_id)
    print(f"Uploaded {{song['filepath']}}: ID {{song_id}}")

# Create playlist
playlist_data = {{
    'date': '{date}',
    'theme': '{theme}',
    'song_ids': json.dumps(song_ids)
}}

response = requests.post(f"{{curl_host}}/api/playlist/create", data=playlist_data, headers=headers)
print(f"{{response.json()}}")

# {command}
"""

folder_path = sys.argv[1] + '/'

# resize images
onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith(".jpg")]
outfiles = []
size = (300, 300)
for image in onlyfiles:
    outfile = folder_path + image.replace('.jpg', '_300.jpg')
    outfiles.append(outfile)
    infile = folder_path + image
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                im.thumbnail(size)
                im.save(outfile, "JPEG")
            os.remove(infile)
        except OSError:
            print("cannot create thumbnail for", infile)
# preview thumbnails
for o in outfiles:
    im = Image.open(o)
    print(im.format, im.size, im.mode)
    im.show()

date, theme = folder_path.split('--')
playlist_date = date.split('/')[-1]
playlist_theme = theme.split('/')[0].replace('-', ' ').title()
print(playlist_date, playlist_theme)

songs = []

mp3files = [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith(".mp3")]
for mp3 in mp3files:
    tag: TinyTag = TinyTag.get(folder_path+mp3)

    title = tag.title.replace('!', '')
    artist = tag.artist.replace('!', '')
    album = tag.album.replace('!', '')
    if not album:
        album = ' '
    album_art = mp3.replace('.mp3', '_300.jpg')
    m,s = divmod(tag.duration, 60)
    seconds = math.floor(s)
    if len(str(seconds)) < 2:
        seconds = str('0'+str(seconds))
    duration = f"{int(m)}:{seconds}"

    song_object = {
        'title': title,
        'artist': artist,
        'duration': duration,
        'album_name': album,
        'album_art': f"{folder_path}{album_art}",
        'filepath': f"{folder_path}{mp3}"
    }
    songs.append(song_object)

command=f"uv run {folder_path}upload_{playlist_date}.py"
script = template.format(
    date=playlist_date,
    theme=playlist_theme,
    songs_list=songs,
    command=command
)

script_path = f"{folder_path}/upload_{playlist_date}.py"
with open(script_path, 'w') as f:
    f.write(script)
os.chmod(script_path, 0o755)

print(command)
