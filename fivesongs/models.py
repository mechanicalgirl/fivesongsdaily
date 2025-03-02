from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    __tablename__ = 'song'

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    filepath = db.Column(db.String, nullable=False)
    duration = db.Column(db.String, nullable=True)
    album_name = db.Column(db.String, nullable=True)
    album_art = db.Column(db.String, nullable=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    created_at = db.Column(db.Date, default=str(date.today()))

class Playlist(db.Model):
    __tablename__ = 'playlist'

    id = db.Column(db.Integer, primary_key=True)
    play_date = db.Column(db.Date)
    created_at = db.Column(db.Date, default=str(date.today()))

