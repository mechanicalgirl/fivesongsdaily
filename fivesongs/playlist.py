from datetime import datetime, timezone
import json

from feedgen.feed import FeedGenerator
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

@bp.route('/today')
def today():
    """ Simple API endpoint for media posting """
    db = get_db()
    playlist = db.execute("SELECT play_date, song_list FROM playlist WHERE play_date = current_date").fetchone()

    song_list = playlist['song_list'].split('<br />')
    play = {
        'playlist_date': str(playlist['play_date']),
        'playlist_songs': song_list
    }
    output = json.loads(json.dumps(play))
    return output

@bp.route('/rss')
def rss():
    fg = FeedGenerator() 
    fg.id('https://www.fivesongsdaily.com')
    fg.title('Five Songs Daily')
    fg.author({'name':'Barbara','email':'barbara@mechanicalgirl.com'})
    fg.link(href='https://www.fivesongsdaily.com', rel='alternate')
    fg.logo('https://www.fivesongsdaily.com/static/images/lgo_main.png')
    fg.subtitle('RSS feed from fivesongsdaily.com')
    fg.link(href='https://www.fivesongsdaily.com', rel='self')
    fg.language('en')

    db = get_db()
    posts_query = "SELECT play_date, song_list FROM playlist WHERE play_date <= current_date ORDER BY play_date DESC LIMIT 10"
    posts = db.execute(posts_query).fetchall()
    
    entries = []
    for p in posts:
        entry = {}
        entry['title'] = str(p['play_date'])
        entry['body_snippet'] = p['song_list']
        date_str = str(p['play_date'])
        datetime_obj = datetime.strptime(date_str, '%Y-%m-%d')
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
        entry['date'] = datetime_obj
        entries.append(entry)
    
    for e in entries:
        fe = fg.add_entry(order="append")
        fe.id()
        fe.title(e['title'])
        fe.link(href=f"https://www.fivesongsdaily.com")
        fe.description(e['body_snippet'])
        fe.published(e['date'])
        
    fg.rss_file('rss.xml')
    rssfeed  = fg.rss_str(pretty=True)
        
    return rssfeed
