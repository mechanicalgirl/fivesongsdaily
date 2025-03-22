from datetime import datetime
import math

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

def pagination():
    db = get_db()
    post_count = db.execute("SELECT count(*) AS count FROM playlist WHERE play_date < current_date;").fetchone()
    total = math.ceil(post_count['count']/3)
    page_list = [int(a) for a in range(1, total+1, 1)]
    return page_list

@bp.route('/playlists')
def playlists():
    page_list = pagination()
    db = get_db()
    playlist_query = "SELECT id, play_date, song_list FROM playlist WHERE play_date < current_date ORDER BY play_date DESC LIMIT 3"
    playlists = db.execute(playlist_query).fetchall()
    return render_template('playlist/playlists.html', playlists=playlists, pagination=page_list)

@bp.route('/pages/<page_number>/')
def pages(page_number):
    page_list = pagination()
    db = get_db()
    total = len(page_list) * 3
    ids = total - ((int(page_number) * 3) - 3)
    page_query = f"SELECT id, play_date, song_list FROM playlist WHERE id <= {ids} AND play_date < current_date ORDER BY play_date DESC LIMIT 3"
    print("PAGE QUERY", page_query)
    playlists = db.execute(page_query).fetchall()
    return render_template('playlist/playlists.html', playlists=playlists, pagination=page_list)

