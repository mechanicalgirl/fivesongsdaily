from datetime import datetime, timedelta, timezone
import json
import time

from feedgen.feed import FeedGenerator
from flask import (
    Blueprint, flash, g, redirect, render_template, request, Response, url_for
)
from user_agents import parse
from werkzeug.exceptions import abort

from fivesongs.auth import login_required
from fivesongs.db import get_db
from fivesongs.extensions import cache


bp = Blueprint('playlist', __name__)

@bp.route('/')
@cache.cached(timeout=300)
def index():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    simple_tracking(user_agent_parsed)
    if user_agent_parsed.is_bot:
        return Response("Not Authorized"), 401
    start = time.time()
    # Move all DB logic into a cached helper function
    playlist_data = get_cached_playlist_data()
    # print(f"PLAYLIST QUERY TOOK {time.time() - start:.3f}s")
    return render_template('playlist/index.html', 
                          songs=playlist_data['songs'],
                          play_date=playlist_data['play_date'],
                          theme=playlist_data['theme'],
                          js_songs=playlist_data['js_songs'])

def simple_tracking(user_agent_parsed):
    insert_query = ("INSERT INTO track (ua, device, os, browser, is_bot, is_email_client, is_mobile, is_pc, is_tablet, is_touch_capable, request_date) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
    db = get_db()
    track_update = db.execute(insert_query, (
        user_agent_parsed.ua_string,
        str(user_agent_parsed.device),
        user_agent_parsed.get_os(),
        user_agent_parsed.get_browser(),
        user_agent_parsed.is_bot,
        user_agent_parsed.is_email_client,
        user_agent_parsed.is_mobile,
        user_agent_parsed.is_pc,
        user_agent_parsed.is_tablet,
        user_agent_parsed.is_touch_capable,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    db.commit()

@cache.cached(timeout=300, key_prefix='playlist_data')
def get_cached_playlist_data():
    db = get_db()
    song_query = """
        SELECT id, artist, title, filepath, duration, album_name, album_art
        FROM song
        WHERE playlist_id = (SELECT id FROM playlist WHERE play_date = current_date)
        ORDER BY id ASC
    """
    db_songs = db.execute(song_query).fetchall()

    # Convert Row objects to dicts for caching
    songs_list = [dict(song) for song in db_songs]

    if db_songs:
        playlist = db.execute("SELECT play_date, theme FROM playlist WHERE play_date = current_date").fetchone()
        play_date = str(playlist['play_date'])
        theme = playlist['theme']
    else:
        song_query = """
            SELECT id, artist, title, filepath, duration, album_name, album_art
            FROM song
            WHERE id IN (1, 2, 3, 4, 5)
            ORDER BY id ASC
        """
        db_songs = db.execute(song_query).fetchall()
        songs_list = [dict(song) for song in db_songs]
        play_date = str(datetime.today().date())
        theme = 'Mermaids'

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

    return {
        'songs': songs_list,
        'play_date': play_date,
        'theme': theme,
        'js_songs': js_songs
    }

@bp.route('/today')
def today():
    """ Simple API endpoint for media posting """
    db = get_db()
    yesterdays_theme = db.execute("SELECT play_date, theme FROM playlist WHERE play_date = DATE('now', '-1 day')").fetchone()
    playlist = db.execute("SELECT play_date, song_list FROM playlist WHERE play_date = current_date").fetchone()
    if not playlist:
        playlist = db.execute("SELECT play_date, song_list, theme FROM playlist WHERE id = 1").fetchone()
    song_list = playlist['song_list'].split('<br />')
    play = {
        'playlist_date': str(playlist['play_date']),
        'playlist_songs': song_list,
        'playlist_theme': yesterdays_theme['theme']
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
