# Django settings for the fivesongs project.

import os, logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)
ADMIN_EMAIL = ''
MANAGERS = ADMINS
DEFAULT_FROM_EMAIL = ''

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'America/Los Angeles'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False

MEDIA_ROOT = '/fivesongs/site_media/'

MEDIA_URL = '/site_media/'

ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = ''

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.project_logging.LoggingMiddleware',
)

ROOT_URLCONF = 'fivesongs.urls'

TEMPLATE_DIRS = (
    '/fivesongs/templates/'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites', 
    'django.contrib.admin', 
    'django.contrib.comments',
    'fivesongs.playlist',
    'fivesongs.profiles',
    'fivesongs.pages',
    'fivesongs.contact',
)

AKISMET_API_KEY = ''

LOGOUT_URL = '/accounts/login/'

LOGGING_LEVEL   = (logging.DEBUG if DEBUG else logging.WARNING)
LOGGING_LOGFILE = '/logs/'+DATABASE_NAME+'.log'
LOGGING_FORMAT  = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_DATEFMT = "%m-%d %H:%M:%S"

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT,
                    datefmt=LOGGING_DATEFMT, filename=LOGGING_LOGFILE, filemode="a")

