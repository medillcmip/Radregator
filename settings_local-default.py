DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
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
MEDIA_URL = ''

# Facebook Application settings for Facebook Connect
FB_API_ID = ''
FB_API_KEY = ''
FB_SECRET_KEY = ''

# If you need to add additional middleware (like using Firelogger)
# Overwrite the MIDDLEWARE_CLASSES variable.  You should probably
# copy over what's in settings.py`
#MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#)

# Enable/disable console logging to Firebug using Firepython
# http://firelogger.binaryage.com 
ENABLE_FIREPYTHON=False
if DEBUG and ENABLE_FIREPYTHON:
    MIDDLEWARE_CLASSES += ('firepython.middleware.FirePythonDjango',)
