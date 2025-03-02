from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from fivesongs.auth import login_required
from fivesongs.db import get_db

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
    ## TODO: if this list comes back empty, return the default list - ids 1-5
    play_date = db.execute("SELECT play_date FROM playlist WHERE play_date = current_date").fetchone()
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

###############################################
# Revisit these later, to work with playlists #
###############################################

"""
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('playlist/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
"""

