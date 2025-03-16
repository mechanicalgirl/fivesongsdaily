from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from fivesongs.auth import login_required
from fivesongs.db import get_db
import json

bp = Blueprint('playlist', __name__)

@bp.route('/')
def index():
    db = get_db()
    song_query = """
        SELECT id, artist, title, filepath, duration, album_name, album_art
        FROM song 
        WHERE playlist_id = (SELECT id FROM playlist WHERE play_date = current_date)
        ORDER BY id ASC
    """
    db_songs = db.execute(song_query).fetchall()

    if db_songs:
        play_date = db.execute("SELECT play_date FROM playlist WHERE play_date = current_date").fetchone()
        play_date = play_date['play_date']
    else:
        song_query = """
            SELECT id, artist, title, filepath, duration, album_name, album_art
            FROM song
            WHERE id IN (1, 2, 3, 4, 5)
            ORDER BY id ASC
        """
        db_songs = db.execute(song_query).fetchall()
        play_date = datetime.today().date()

    js_songs = []
    for song in db_songs:
        js_song = {
            "name": song['title'],
            "artist": song['artist'],
            "album": song['album_name'],
            "url": f"/static/musicfiles/{song['filepath']}",
            "cover_art_url": f"/static/albumart/{song['album_art']}"
        }
        js_songs.append(js_song)

    return render_template('playlist/index.html', songs=db_songs, play_date=play_date, js_songs=js_songs)
    return render_template(
        'playlist/index.html.jinja',
        songs=db_songs, play_date=play_date, js_songs=json.dumps(js_songs))
