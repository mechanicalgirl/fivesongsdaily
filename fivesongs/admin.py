import os
import sys

from flask import (
    Blueprint, current_app, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from fivesongs.auth import login_required
from fivesongs.db import get_db

bp = Blueprint('admin', __name__)

@bp.route('/admin')
# @login_required
def admin():
    db = get_db()
    song_query = """
        SELECT id, artist, title
        FROM song 
        ORDER BY id DESC
        LIMIT 10
    """
    db_songs = db.execute(song_query).fetchall()

    # TODO: alert on any empty playlists
    playlist_query = """
        SELECT id, play_date, created_at
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
            'songs': []
        }
        p_songs = db.execute(f"SELECT title, artist FROM song WHERE playlist_id = {p['id']}").fetchall()
        for s in p_songs:
            playlist['songs'].append(f"{s['title']} - {s['artist']}")
        all_playlists.append(playlist)
    return render_template('admin/index.html', songs=db_songs, playlists=all_playlists)

@bp.route('/admin/songs')
# @login_required
def songs():
    """ List all songs """
    db = get_db()
    song_query = """
        SELECT id, artist, title, playlist_id
        FROM song
        ORDER BY id DESC
    """
    db_songs = db.execute(song_query).fetchall()
    return render_template('admin/songs.html', songs=db_songs)

@bp.route('/admin/playlists')
# @login_required
def playlists():
    # TODO: alert on any empty playlists
    db = get_db()
    playlist_query = """
        SELECT id, play_date, created_at
        FROM playlist
        ORDER BY play_date DESC
    """
    db_playlists = db.execute(playlist_query).fetchall()
    all_playlists = []
    for p in db_playlists:
        playlist = {
            'id': p['id'],
            'play_date': p['play_date'],
            'songs': []
        }
        p_songs = db.execute(f"SELECT title, artist FROM song WHERE playlist_id = {p['id']}").fetchall()
        for s in p_songs:
            playlist['songs'].append(f"{s['title']} - {s['artist']}")
        all_playlists.append(playlist)
    return render_template('admin/playlists.html', playlists=all_playlists)

@bp.route('/admin/song/<int:id>')
# @login_required
def song(id):
    """ Display all metadata for a single song; link to edit page """
    ## TODO: add delete option for a single song
    db = get_db()
    song_query = f"SELECT id, artist, title, filepath, duration, album_name, album_art, playlist_id, created_at FROM song WHERE id = {id}"
    db_song = db.execute(song_query).fetchone()
    play_date = ''
    if db_song['playlist_id']:
        play_date = db.execute(f"SELECT play_date FROM playlist WHERE id = {db_song['playlist_id']}").fetchone()
    return render_template('admin/song.html', song=db_song, play_date=play_date)

MP3_UPLOAD_FOLDER = '/Users/barbarashaurette/Documents/code/fivesongsdaily/fivesongs/static/musicfiles'
MP3_ALLOWED_EXTENSIONS = {'mp3'}
ALBUMART_UPLOAD_FOLDER = '/Users/barbarashaurette/Documents/code/fivesongsdaily/fivesongs/static/albumart'
ALBUMART_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(type, filename):
    if type == 'song':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in MP3_ALLOWED_EXTENSIONS
    if type == 'albumart':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALBUMART_ALLOWED_EXTENSIONS

@bp.route('/admin/song/edit/<int:id>', methods=('GET', 'POST'))
# @login_required
def songedit(id):
    """ Get and process the song edit form """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form
        songfile = request.files['filepath']
        albumartfile = request.files['album_art']

        ## TODO: stop the overwrite of both files when either a new song file or album art is uploaded

        if songfile and allowed_file('song', songfile.filename):
            filename = secure_filename(songfile.filename)
            songfile.save(os.path.join(MP3_UPLOAD_FOLDER, filename))

        if albumartfile and allowed_file('albumart', albumartfile.filename):
            filename = secure_filename(albumartfile.filename)
            albumartfile.save(os.path.join(ALBUMART_UPLOAD_FOLDER, filename))

        update_query = (f"UPDATE song SET title='{form_data['title']}', "
                        f"artist='{form_data['artist']}', "
                        f"duration='{form_data['duration']}', "
                        f"album_name='{form_data['album_name']}', "
                        f"filepath = '{songfile.filename}', "
                        f"album_art = '{albumartfile.filename}' "
                        f"WHERE id = {id} RETURNING id;")
        song_update = db.execute(update_query).fetchone()
        db.commit()
        return redirect('/admin/songs', 302)
    else:
        song_query = f"SELECT id, artist, title, filepath, duration, album_name, album_art, playlist_id, created_at FROM song WHERE id = {id}"
        db_song = db.execute(song_query).fetchone()
        play_date = ''
        if db_song['playlist_id']:
            play_date = db.execute(f"SELECT play_date FROM playlist WHERE id = {db_song['playlist_id']}").fetchone()
        return render_template('admin/songedit.html', song=db_song, play_date=play_date)

@bp.route('/admin/song/create', methods=('GET', 'POST'))
# @login_required
def songcreate(): 
    """ Get and process the song create form """
    # https://flask.palletsprojects.com/en/stable/patterns/fileuploads/

    if request.method == 'POST':
        form_data = request.form
        songfile = request.files['filepath']
        albumartfile = request.files['album_art']

        if songfile and allowed_file('song', songfile.filename):
            filename = secure_filename(songfile.filename)
            songfile.save(os.path.join(MP3_UPLOAD_FOLDER, filename))

        if albumartfile and allowed_file('albumart', albumartfile.filename):
            filename = secure_filename(albumartfile.filename)
            albumartfile.save(os.path.join(ALBUMART_UPLOAD_FOLDER, filename))

        song_filepath = songfile.filename.replace(' ', '_')
        albumart_filepath = albumartfile.filename.replace(' ', '_')
        try:
            insert_query = (f"INSERT INTO song (title, artist, duration, album_name, filepath, album_art) "
                            f"VALUES('{form_data['title']}', '{form_data['artist']}', "
                            f"'{form_data['duration']}', '{form_data['album_name']}', "
                            f"'{song_filepath}', '{albumart_filepath}' ) "
                            f"RETURNING id;")
            print(insert_query)
            db = get_db()
            song_update = db.execute(insert_query).fetchone()
            db.commit()
        except Exception as e:
            return render_template('admin/songerror.html', error=e)
        
        # return to /admin/song/{new song id}
        return redirect('/admin/songs', 302)
    else:
        # display an empty song form
        return render_template('admin/songcreate.html')

@bp.route('/admin/song/delete/<int:id>', methods=["POST"])
# @login_required
def songdelete(id):
    """ Process song deletion """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form
        delete_query = f"DELETE FROM song WHERE id = {id} RETURNING id;"
        song_delete = db.execute(delete_query).fetchone()
        db.commit()
        return redirect('/admin/songs', 302)
    else:
        return redirect('/admin/songs', 302)

@bp.route('/admin/playlist/<int:id>', methods=('GET', 'POST'))
# @login_required
def playlist(id):
    """ Display all metadata for a single playlist; link to edit page """
    db = get_db()
    playlist_query = f"SELECT id, play_date, created_at FROM playlist WHERE id = {id}"
    db_playlist = db.execute(playlist_query).fetchone()
    song_query = f"SELECT id, artist, title, filepath, album_art FROM song WHERE playlist_id = {id} ORDER BY id ASC"
    db_songs = db.execute(song_query).fetchall()
    return render_template('admin/playlist.html', songs=db_songs, playlist=db_playlist)

@bp.route('/admin/playlist/edit/<int:id>', methods=('GET', 'POST'))
# @login_required
def playlistedit(id):
    """ Get and process the playlist edit form """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form
        song_ids = [int(form_data[x]) for x in form_data]
        update_query = f"UPDATE song SET playlist_id = {id} WHERE id IN {tuple(song_ids)} RETURNING NULL"
        print(update_query)
        playlist_update = db.execute(update_query).fetchone()
        db.commit()
        return redirect('/admin/playlists', 302)
    else:
        playlist_query = f"SELECT id, play_date, created_at FROM playlist WHERE id = {id}"
        db_playlist = db.execute(playlist_query).fetchone()
        song_query = f"SELECT id, artist, title, filepath, album_art FROM song WHERE playlist_id = {id} ORDER BY id ASC"
        db_songs = db.execute(song_query).fetchall()
        all_songs = db.execute("SELECT id, artist, title, filepath, album_art FROM song ORDER BY id ASC").fetchall()
        return render_template('admin/playlistedit.html', songs=db_songs, playlist=db_playlist, all_songs=all_songs)

# TODO: validate so that the same group of songs cannot be on more than one playlist?

@bp.route('/admin/playlist/create', methods=('GET', 'POST'))
# @login_required
def playlistcreate():
    """ Get and process the playlist create form """
    if request.method == 'POST':
        form_data = request.form

        db = get_db()
        try:
            db = get_db()
            insert_query = f"INSERT INTO playlist (play_date) VALUES('{form_data['play_date']}') RETURNING id"
            print(insert_query)
            playlist_create = db.execute(insert_query).fetchone()
            db.commit()
            print(playlist_create['id'])

            playlist_id = playlist_create['id']

            # also do the song update with the new playlist id
            song_ids = [int(form_data[x]) for x in form_data if x.startswith('song-id-')]
            update_query = f"UPDATE song SET playlist_id = {playlist_id} WHERE id IN {tuple(song_ids)} RETURNING NULL"
            print(update_query)
            songs_update = db.execute(update_query).fetchone()
            db.commit()
            return redirect(f"/admin/playlist/{playlist_id}", 302)

        except Exception as e:
            return render_template('admin/playlisterror.html', error=e)

        return redirect('/admin/playlists', 302)
    else:
        # display an empty playlist form
        db = get_db()
        all_songs = db.execute("SELECT id, artist, title, filepath, album_art FROM song ORDER BY id ASC").fetchall()
        return render_template('admin/playlistcreate.html', all_songs=all_songs)

@bp.route('/admin/playlist/delete/<int:id>', methods=["POST"])
# @login_required
def playlistdelete(id):
    """ Process playlist deletion """
    db = get_db()
    if request.method == 'POST':
        form_data = request.form
        delete_query = f"DELETE FROM playlist WHERE id = {id} RETURNING id;"
        playlist_delete = db.execute(delete_query).fetchone()
        db.commit()
        update_query = f"UPDATE song SET playlist_id = NULL WHERE playlist_id = {id};"
        song_update = db.execute(update_query).fetchall()
        return redirect('/admin/playlists', 302)
    else:
        return redirect('/admin/playlists', 302)
