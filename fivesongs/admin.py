import ast
import json
import math
import os
import sys

from flask import (
    Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, Response, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from fivesongs.auth import login_required
from fivesongs.db import get_db
from fivesongs.extensions import cache

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'fivesongs/static')
MP3_ALLOWED_EXTENSIONS = {'mp3'}
ALBUMART_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

bp = Blueprint('admin', __name__)

@bp.route('/admin/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    cache.clear()
    print('Cache cleared successfully!', 'success')
    return redirect(url_for('admin.admin'))

def pagination():
    db = get_db()
    post_count = db.execute("SELECT count(*) AS count FROM playlist;").fetchone()
    total = math.ceil(post_count['count']/20)
    page_list = [int(a) for a in range(1, total+1, 1)]
    # PAGE LIST [1, 2, 3]
    return page_list

@bp.route('/admin')
@login_required
@cache.cached(timeout=60)
def admin():

    db = get_db()
    song_query = """
        SELECT id, artist, title, created_at
        FROM song
        ORDER BY id DESC
        LIMIT 10
    """
    db_songs = db.execute(song_query).fetchall()

    playlist_query = """
        SELECT id, play_date, song_list, created_at, theme
        FROM playlist
        ORDER BY play_date DESC
        LIMIT 10
    """
    db_playlists = db.execute(playlist_query).fetchall()
    all_playlists = []
    for p in db_playlists:
        playlist = {
            'id': p['id'],
            'play_date': p['play_date'],
            'created_at': p['created_at'],
            'songs': [],
            'song_list': p['song_list'],
            'theme': p['theme'],
            'alert': False
        }
        p_songs = db.execute("SELECT title, artist FROM song WHERE playlist_id = ?", (p['id'],)).fetchall()
        for s in p_songs:
            playlist['songs'].append(f"{s['title']} - {s['artist']}")
        if len(playlist['songs']) < 5:
            playlist['alert'] = True
        all_playlists.append(playlist)
    return render_template('admin/index.html', songs=db_songs, playlists=all_playlists)

@bp.route('/admin/songs')
@login_required
@cache.cached(timeout=60)
def songs():
    """ List all songs """
    db = get_db()
    song_query = """
        SELECT id, artist, title, playlist_id, created_at
        FROM song
        ORDER BY id DESC
    """
    db_songs = db.execute(song_query).fetchall()
    return render_template('admin/songs.html', songs=db_songs)

@bp.route('/admin/playlists')
@login_required
@cache.cached(timeout=60)
def playlists():
    # all playlists, first page
    page_list = pagination()
    db = get_db()

    playlist_query = """
        SELECT id, play_date, created_at, song_list, theme
        FROM playlist
        ORDER BY play_date DESC
        LIMIT 20
    """
    db_playlists = db.execute(playlist_query).fetchall()
    all_playlists = []
    for p in db_playlists:
        playlist = {
            'id': p['id'],
            'play_date': p['play_date'],
            'created_at': p['created_at'],
            'song_list': p['song_list'],
            'theme': p['theme'],
            'songs': []
        }
        p_songs = db.execute("SELECT title, artist FROM song WHERE playlist_id = ?", (p['id'],)).fetchall()
        for s in p_songs:
            playlist['songs'].append(f"{s['title']} - {s['artist']}")
        if len(playlist['songs']) < 5:
            playlist['alert'] = True
        all_playlists.append(playlist)
    return render_template('admin/playlists.html', playlists=all_playlists, pagination=page_list)

@bp.route('/admin/playlists/pages/<page_number>')
@cache.cached(timeout=60)
def pages(page_number):
    # all playlists, paginated
    page_list = pagination()
    db = get_db()

    limit = 20
    offset = ((int(page_number)-1) * 20)
    print(page_number, limit, offset)

    playlist_query = "SELECT id, play_date, created_at, song_list, theme FROM playlist ORDER BY play_date DESC LIMIT ? OFFSET ?"
    db_playlists = db.execute(playlist_query, (limit, offset)).fetchall()
    all_playlists = []
    for p in db_playlists:
        playlist = {
            'id': p['id'],
            'play_date': p['play_date'],
            'created_at': p['created_at'],
            'song_list': p['song_list'],
            'theme': p['theme'],
            'songs': []
        }
        p_songs = db.execute("SELECT title, artist FROM song WHERE playlist_id = ?", (p['id'],)).fetchall()
        for s in p_songs:
            playlist['songs'].append(f"{s['title']} - {s['artist']}")
        if len(playlist['songs']) < 5:
            playlist['alert'] = True
        all_playlists.append(playlist)
    return render_template('admin/playlists.html', playlists=all_playlists, pagination=page_list)

@bp.route('/admin/playlists/search', methods=('GET', 'POST'))
@login_required
def searchplaylists():
    # search playlist song lists
    if request.method == 'POST':
        form_data = request.form
        searchterm = form_data['searchterm']
        db = get_db()
        playlist_query = "SELECT id, play_date, created_at, song_list, theme FROM playlist WHERE song_list LIKE ? ORDER BY play_date DESC"
        db_playlists = db.execute(playlist_query, (f'%{searchterm}%',)).fetchall()
    else:
        # display an empty search form
        db_playlists = None
    return render_template('admin/playlistssearch.html', playlists=db_playlists)

@bp.route('/admin/song/<int:id>')
@login_required
def song(id):
    """ Display all metadata for a single song; link to edit page """
    db = get_db()
    song_query = "SELECT id, artist, title, filepath, duration, album_name, album_art, playlist_id, created_at FROM song WHERE id = ?"
    db_song = db.execute(song_query, (id,)).fetchone()
    play_date = ''
    if db_song['playlist_id']:
        play_date = db.execute("SELECT play_date FROM playlist WHERE id = ?", (db_song['playlist_id'],)).fetchone()
    return render_template('admin/song.html', song=db_song, play_date=play_date)

def allowed_file(type, filename):
    if type == 'song':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in MP3_ALLOWED_EXTENSIONS
    if type == 'albumart':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALBUMART_ALLOWED_EXTENSIONS

@bp.route('/admin/tracking')
@login_required
def track():
    db = get_db()
    sel_query = ("SELECT ua, device, os, browser, is_bot, is_email_client, is_mobile, is_pc, is_tablet, is_touch_capable, request_date FROM track;")
    tracking = db.execute(sel_query).fetchall()
    return render_template('admin/track.html', tracking=tracking)

@bp.route('/admin/song/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def songedit(id):
    """ Get and process the song edit form """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form

        songfile = request.files['filepath']
        albumartfile = request.files['album_art']

        # Build update query dynamically based on what's being updated
        update_fields = []
        update_values = []

        if songfile and allowed_file('song', songfile.filename):
            filename = secure_filename(songfile.filename)
            songfile.save(os.path.join(UPLOAD_FOLDER + '/musicfiles', filename))
            update_fields.append("filepath = ?")
            update_values.append(songfile.filename)

        if albumartfile and allowed_file('albumart', albumartfile.filename):
            filename = secure_filename(albumartfile.filename)
            albumartfile.save(os.path.join(UPLOAD_FOLDER + '/albumart', filename))
            update_fields.append("album_art = ?")
            update_values.append(albumartfile.filename)

        # Add standard fields
        update_fields.extend(["title = ?", "artist = ?", "duration = ?", "album_name = ?"])
        update_values.extend([
            form_data['title'],
            form_data['artist'],
            form_data['duration'],
            form_data['album_name']
        ])

        # Add id for WHERE clause
        update_values.append(id)

        update_query = f"UPDATE song SET {', '.join(update_fields)} WHERE id = ? RETURNING id;"
        song_update = db.execute(update_query, tuple(update_values)).fetchone()
        db.commit()
        return redirect('/admin/songs', 302)
    else:
        song_query = "SELECT id, artist, title, filepath, duration, album_name, album_art, playlist_id, created_at FROM song WHERE id = ?"
        db_song = db.execute(song_query, (id,)).fetchone()
        play_date = ''
        if db_song['playlist_id']:
            play_date = db.execute("SELECT play_date FROM playlist WHERE id = ?", (db_song['playlist_id'],)).fetchone()
        return render_template('admin/songedit.html', song=db_song, play_date=play_date)

@bp.route('/admin/song/create', methods=('GET', 'POST'))
@login_required
def songcreate():
    """ Get and process the song create form """
    # https://flask.palletsprojects.com/en/stable/patterns/fileuploads/

    if request.method == 'POST':
        form_data = request.form
        songfile = request.files['filepath']
        albumartfile = request.files['album_art']

        if songfile and allowed_file('song', songfile.filename):
            filename = secure_filename(songfile.filename)
            songfile.save(os.path.join(UPLOAD_FOLDER + '/musicfiles', filename))

        if albumartfile and allowed_file('albumart', albumartfile.filename):
            filename = secure_filename(albumartfile.filename)
            albumartfile.save(os.path.join(UPLOAD_FOLDER + '/albumart', filename))
            albumart_filepath = albumartfile.filename.replace(' ', '_')
        else:
            albumart_filepath = 'album_default.jpg'

        song_filepath = songfile.filename.replace(' ', '_')
        try:
            insert_query = ("INSERT INTO song (title, artist, duration, album_name, filepath, album_art) "
                            "VALUES(?, ?, ?, ?, ?, ?) "
                            "RETURNING id;")
            db = get_db()
            song_update = db.execute(insert_query, (
                form_data['title'],
                form_data['artist'],
                form_data['duration'],
                form_data['album_name'],
                song_filepath,
                albumart_filepath
            )).fetchone()
            song_id = song_update['id']
            db.commit()
            return redirect(f"/admin/song/{song_id}", 302)
        except Exception as e:
            return render_template('admin/songerror.html', error=e)
    else:
        # display an empty song form
        return render_template('admin/songcreate.html')

@bp.route('/admin/song/delete/<int:id>', methods=["POST"])
@login_required
def songdelete(id):
    """ Process song deletion """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form

        try:
            song_metadata = db.execute("SELECT filepath, album_art FROM song WHERE id = ?", (id,)).fetchone()
            os.remove(os.path.join(UPLOAD_FOLDER + '/musicfiles', song_metadata['filepath']))
            os.remove(os.path.join(UPLOAD_FOLDER + '/albumart', song_metadata['album_art']))
        except Exception as e:
            print(e)

        delete_query = "DELETE FROM song WHERE id = ? RETURNING id;"
        song_delete = db.execute(delete_query, (id,)).fetchone()
        db.commit()
        return redirect('/admin/songs', 302)
    else:
        return redirect('/admin/songs', 302)

@bp.route('/admin/playlist/<int:id>', methods=('GET', 'POST'))
@login_required
def playlist(id):
    """ Display all metadata for a single playlist; link to edit page """
    db = get_db()
    playlist_query = "SELECT id, play_date, created_at, song_list, theme FROM playlist WHERE id = ?"
    db_playlist = db.execute(playlist_query, (id,)).fetchone()
    song_query = "SELECT id, artist, title, filepath, album_art FROM song WHERE playlist_id = ? ORDER BY id ASC"
    db_songs = db.execute(song_query, (id,)).fetchall()
    return render_template('admin/playlist.html', songs=db_songs, playlist=db_playlist)

@bp.route('/admin/playlist/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def playlistedit(id):
    """ Get and process the playlist edit form """
    db = get_db()
    if request.method == 'POST':
        form_data = {**request.form}
        play_date = form_data['play_date']
        theme = form_data['theme']
        del form_data['play_date']
        del form_data['theme']
        song_ids = [int(form_data[x]) for x in form_data]
        playlist_id = id

        clear_query = "UPDATE song SET playlist_id = NULL WHERE playlist_id = ? RETURNING NULL"
        playlist_clear = db.execute(clear_query, (id,)).fetchone()
        db.commit()

        # Create placeholders for IN clause
        placeholders = ','.join('?' * len(song_ids))
        song_update_query = f"UPDATE song SET playlist_id = ? WHERE id IN ({placeholders}) RETURNING NULL"
        song_update = db.execute(song_update_query, (id, *song_ids)).fetchone()
        db.commit()

        list_update_query = "UPDATE playlist SET play_date = ? WHERE id = ? RETURNING NULL"
        playlist_update = db.execute(list_update_query, (play_date, id)).fetchone()
        db.commit()

        songs = []
        song_list_query = f"SELECT artist, title FROM song WHERE id IN ({placeholders})"
        song_list_update = db.execute(song_list_query, tuple(song_ids)).fetchall()
        for s in song_list_update:
            song = f"{s['artist']} - {s['title']}"
            songs.append(song)
        song_list = "<br />".join(map(str, songs))

        playlist_update_query = "UPDATE playlist SET song_list = ?, theme = ? WHERE id = ? RETURNING NULL"
        playlist_update = db.execute(playlist_update_query, (song_list, theme, playlist_id)).fetchone()
        db.commit()

        return redirect(f"/admin/playlist/{id}", 302)
    else:
        playlist_query = "SELECT id, play_date, created_at, theme FROM playlist WHERE id = ?"
        db_playlist = db.execute(playlist_query, (id,)).fetchone()

        song_query = "SELECT id, artist, title, filepath, album_art FROM song WHERE playlist_id = ? ORDER BY id ASC"
        db_songs = db.execute(song_query, (id,)).fetchall()

        n = 5-len(db_songs)
        extra = [x + len(db_songs) for x in list(range(n))]

        all_songs = db.execute("SELECT id, artist, title, filepath, album_art FROM song ORDER BY created_at DESC").fetchall()

        return render_template('admin/playlistedit.html', songs=db_songs, playlist=db_playlist, all_songs=all_songs, extra=extra)

@bp.route('/admin/playlist/create', methods=('GET', 'POST'))
@login_required
def playlistcreate():
    """ Get and process the playlist create form """
    if request.method == 'POST':
        form_data = request.form
        db = get_db()
        theme = form_data['theme']
        try:
            insert_query = "INSERT INTO playlist (play_date) VALUES(?) RETURNING id"
            playlist_create = db.execute(insert_query, (form_data['play_date'],)).fetchone()
            db.commit()

            playlist_id = playlist_create['id']

            # also do the song update with the new playlist id
            try:
                song_ids = [int(form_data[x]) for x in form_data if x.startswith('song-id-')]
                placeholders = ','.join('?' * len(song_ids))
                update_query = f"UPDATE song SET playlist_id = ? WHERE id IN ({placeholders}) RETURNING NULL"
                songs_update = db.execute(update_query, (playlist_id, *song_ids)).fetchone()
                db.commit()
            except Exception as e:
                print("SONGS UPDATE", e)
                ## This will hit if there are fewer then five songs: invalid literal for int() with base 10: ''

            # also update the playlist with the new song_list
            try:
                songs = []
                song_list_query = f"SELECT artist, title FROM song WHERE id IN ({placeholders})"
                song_list_update = db.execute(song_list_query, tuple(song_ids)).fetchall()
                for s in song_list_update:
                    song = f"{s['artist']} - {s['title']}"
                    songs.append(song)
                song_list = "<br />".join(map(str, songs))

                playlist_update_query = "UPDATE playlist SET song_list = ?, theme = ? WHERE id = ? RETURNING NULL"
                playlist_update = db.execute(playlist_update_query, (song_list, theme, playlist_id)).fetchone()
                db.commit()
            except Exception as e:
                print("SONG LIST UPDATE", e)
                ## If the previous block errors, we also get this: local variable 'song_ids' referenced before assignment

            return redirect(f"/admin/playlist/{playlist_id}", 302)

        except Exception as e:
            return render_template('admin/playlisterror.html', error=e)

        return redirect('/admin/playlists', 302)
    else:
        # display an empty playlist form
        db = get_db()
        all_songs = db.execute("SELECT id, artist, title, filepath, album_art FROM song ORDER BY id DESC").fetchall()
        return render_template('admin/playlistcreate.html', all_songs=all_songs)

@bp.route('/admin/playlist/delete/<int:id>', methods=["POST"])
@login_required
def playlistdelete(id):
    """ Process playlist deletion """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form
        delete_query = "DELETE FROM playlist WHERE id = ? RETURNING id;"
        playlist_delete = db.execute(delete_query, (id,)).fetchone()
        db.commit()
        update_query = "UPDATE song SET playlist_id = NULL WHERE playlist_id = ?;"
        song_update = db.execute(update_query, (id,)).fetchall()
        return redirect('/admin/playlists', 302)
    else:
        return redirect('/admin/playlists', 302)

@bp.route('/api/playlist/create', methods=["POST"])
def playlist_create_endpoint():
    """ Process incoming playlist metadata """
    if request.method == 'POST':
        errors = []
        song_list = ''
        db = get_db()
        if not (request.headers['Flask-Key'] and request.headers['Auth-Name']):
            return Response("Not Authorized"), 401
        key = db.execute("SELECT password FROM user WHERE username = ?", (request.headers['Auth-Name'],)).fetchone()
        if not request.headers['Flask-Key'] == key['password']:
            return Response("Not Authorized"), 401

        form_data = request.form
        playlist_theme = form_data['theme']
        playlist_date = form_data['date']
        playlist_songs = form_data['song_ids']

        insert_query = "INSERT INTO playlist (play_date, theme) VALUES(?, ?) RETURNING id"
        playlist_create = db.execute(insert_query, (playlist_date, playlist_theme,)).fetchone()
        db.commit()

        playlist_id = playlist_create['id']

        # update songs with the new playlist id
        try:
            song_ids = ast.literal_eval(playlist_songs)
            placeholders = ','.join('?' * len(song_ids))
            update_query = f"UPDATE song SET playlist_id = ? WHERE id IN ({placeholders}) RETURNING NULL"
            songs_update = db.execute(update_query, (playlist_id, *song_ids)).fetchone()
            db.commit()
        except Exception as e:
            errors.append(f"SONGS UPDATE {e}")
            ## This will hit if there are fewer then five songs: invalid literal for int() with base 10: ''

        # update the playlist with the new song_list
        try:
            songs = []
            song_list_query = f"SELECT artist, title FROM song WHERE id IN ({placeholders})"
            song_list_update = db.execute(song_list_query, tuple(song_ids)).fetchall()
            for s in song_list_update:
                song = f"{s['artist']} - {s['title']}"
                songs.append(song)
            song_list = "<br />".join(map(str, songs))

            playlist_update_query = "UPDATE playlist SET song_list = ? WHERE id = ? RETURNING NULL"
            playlist_update = db.execute(playlist_update_query, (song_list, playlist_id)).fetchone()
            db.commit()
        except Exception as e:
            errors.append(f"SONG LIST UPDATE {e}")
            ## If the previous block errors, we also get this: local variable 'song_ids' referenced before assignment

        playlist_object = {
            'id': playlist_id,
            'theme': playlist_theme,
            'date': playlist_date,
            'song_list': song_list,
            'errors': errors
        }
    if errors:
        return Response(str(errors)), 200
    else:
        return Response(json.dumps(playlist_object)), 200

@bp.route('/api/song/create', methods=["POST"])
def song_endpoint():
    """ Process incoming song uploads """
    if request.method == 'POST':
        db = get_db()
        if not (request.headers['Flask-Key'] and request.headers['Auth-Name']):
            return Response("Not Authorized"), 401
        key = db.execute("SELECT password FROM user WHERE username = ?", (request.headers['Auth-Name'],)).fetchone()
        if not request.headers['Flask-Key'] == key['password']:
            return Response("Not Authorized"), 401

        form_data = request.form
        songfile = request.files['filepath']
        albumartfile = request.files['album_art']

        if songfile and allowed_file('song', songfile.filename):
            filename = secure_filename(songfile.filename)
            songfile.save(os.path.join(UPLOAD_FOLDER + '/musicfiles', filename))

        if albumartfile and allowed_file('albumart', albumartfile.filename):
            filename = secure_filename(albumartfile.filename)
            albumartfile.save(os.path.join(UPLOAD_FOLDER + '/albumart', filename))
            albumart_filepath = albumartfile.filename.replace(' ', '_')
        else:
            albumart_filepath = 'album_default.jpg'

        song_filepath = songfile.filename.replace(' ', '_')
        try:
            insert_query = ("INSERT INTO song (title, artist, duration, album_name, filepath, album_art) "
                            "VALUES(?, ?, ?, ?, ?, ?) "
                            "RETURNING id;")
            song_update = db.execute(insert_query, (
                form_data['title'],
                form_data['artist'],
                form_data['duration'],
                form_data['album_name'],
                song_filepath,
                albumart_filepath
            )).fetchone()
            song_id = song_update['id']
            db.commit()
            song_object = {
                'title': form_data['title'],
                'artist': form_data['artist'],
                'duration': form_data['duration'],
                'album_name': form_data['album_name'],
                'filepath': song_filepath,
                'album_art': albumart_filepath,
                'song_id': song_id,
                'url': f"https://fivesongsdaily.com/admin/song/{song_id}"
            }
            return Response(json.dumps(song_object)), 200
        except Exception as e:
            return Response(str(e)), 200

@bp.route('/api/songs/delete', methods=["POST"])
def song_delete_endpoint():
    """ Process incoming song deletions by playlist id """
    if not request.headers['Flask-Key']:
        return Response("Not Authorized"), 401
    if request.method == 'POST':
        db = get_db()
        if not (request.headers['Flask-Key'] and request.headers['Auth-Name']):
            return Response("Not Authorized"), 401
        key = db.execute("SELECT password FROM user WHERE username = ?", (request.headers['Auth-Name'],)).fetchone()
        if not request.headers['Flask-Key'] == key['password']:
            return Response("Not Authorized"), 401

        form_data = request.form
        playlist_id = int(form_data['playlist_id'])

        song_objects = {
            'filepath': [],
            'album_art': [],
            'song_id': [],
            'status': ''
        }

        song_query = "SELECT id, filepath, album_art FROM song WHERE playlist_id = ? ORDER BY id ASC"
        db_songs = db.execute(song_query, (playlist_id,)).fetchall()
        if not db_songs:
            song_objects['status'] = f"Songs from playlist {playlist_id} not found"
            return Response(json.dumps(song_objects)), 200

        try:
            for song in db_songs:
                os.remove(os.path.join(UPLOAD_FOLDER + '/musicfiles', song['filepath']))
                song_objects['filepath'].append(song['filepath'])
                os.remove(os.path.join(UPLOAD_FOLDER + '/albumart', song['album_art']))
                song_objects['album_art'].append(song['album_art'])
                delete_query = "DELETE FROM song WHERE id = ? RETURNING id;"
                song_delete = db.execute(delete_query, (song['id'],)).fetchone()
                db.commit()
                song_objects['song_id'].append(song['id'])
                song_objects['status'] = f"Songs from playlist {playlist_id} deleted"
            return Response(json.dumps(song_objects)), 200
        except Exception as e:
            print(e)
            return Response(str(e)), 200
