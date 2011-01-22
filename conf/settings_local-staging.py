DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'medill2010_radregator_staging', # Or path to database file if using sqlite3.
        'USER': 'medill2010_radregator_staging', # Not used with sqlite3.
        'PASSWORD': 'FAB_REPL_DB_PASSWORD',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://staging.medill2010.webfactional.com/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://staging.medill2010.webfactional.com/static/admin/'

# Facebook Application settings for Facebook Connect
FB_API_ID = 'FAB_REPL_FB_API_ID'
FB_API_KEY = 'FAB_REPL_FB_API_KEY'
FB_SECRET_KEY = 'FAB_REPL_FB_SECRET_KEY'

EMAIL_HOST = 'FAB_REPL_EMAIL_HOST'
EMAIL_HOST_USER = 'FAB_REPL_EMAIL_HOST_USER'
EMAIL_HOST_PASSWORD = 'FAB_REPL_EMAIL_HOST_PASS'
DEFAULT_FROM_EMAIL = 'FAB_REPL_EMAIL_ADDR'
SERVER_EMAIL = 'FAB_REPL_EMAIL_ADDR'


# If you need to add additional middleware (like using Firelogger)
# Overwrite the MIDDLEWARE_CLASSES variable.  You should probably
# copy over what's in settings.py
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Overwrite the installed apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'core',
    'tagger',
    'clipper',
    'users',

    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    # Enable south for schema migration
    'south'
)

# Enable/disable console logging to Firebug using Firepython
# http://firelogger.binaryage.com 
ENABLE_FIREPYTHON=True
if DEBUG and ENABLE_FIREPYTHON:
    MIDDLEWARE_CLASSES += ('firepython.middleware.FirePythonDjango',)


# Set to True to show uncaught exceptions in the runserver window.
# Don't use this in a production environment
# See http://stackoverflow.com/questions/690723/log-all-errors-to-console-or-file-on-django-site/691252#691252
if DEBUG:
    DEBUG_PROPAGATE_EXCEPTIONS = False 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Location of application log file.
LOG_FILENAME = "/home/medill2010/logs/user/sourcerer-staging.log"

# How often log files should be rotated
# See Python documentation for TimedRotatingFileHandle for possible values.
# Default is daily rotation.
LOG_INTERVAL = 'D'

# Maximum number of logs to save.  If this number is exceeded, the oldest
# log will be overwritten. If set to 0, an unlimited  number of logs is saved.
LOG_BACKUP_COUNT = 30

# Log level.  Can be 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'.
LOG_LEVEL='WARNING'
