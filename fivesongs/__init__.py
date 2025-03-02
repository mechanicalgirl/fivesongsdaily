import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(name='fivesongs', template_mode='bootstrap4')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(12),
        DATABASE=os.path.join(app.instance_path, 'fivesongs.sqlite3'),
        FLASK_ADMIN_SWATCH='cerulean'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    admin.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import playlist
    app.register_blueprint(playlist.bp)
    app.add_url_rule('/', endpoint='index')

    # Add model views
    from .models import Song, Playlist
    # admin.add_view(ModelView(Song, db.session))
    # admin.add_view(ModelView(Playlist, db.session))

    return app
