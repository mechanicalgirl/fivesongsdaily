fivesongsdaily
===============

Flask app for managing and displaying daily music playlists

## Setup

### 1. One-time venv creation:

```sh
python3 -m venv venv
```

### 2. Activate virtualenv

```sh
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 3. Initialize the database

```sh
flask --app fivesongs init-db
```

### 5. Start the application

**Development** (with auto-reload):
```sh
flask --app fivesongs run --debug
```

**Production** (with uWSGI):
```sh
uwsgi uwsgi.ini
```

The application will be available at:
- Development: http://127.0.0.1:5000
- Production (uWSGI): http://127.0.0.1:1024
