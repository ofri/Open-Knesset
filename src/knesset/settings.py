# Django settings for knesset project.
import sys, socket, os
hostname = socket.gethostname() # to add host specific overrides

base_dir = os.path.abspath(os.path.dirname(__file__))  # used instead of relative path, so that importing this module from outside would work (like done in update_db.py)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'         # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'knesset'  # Or path to database file if using sqlite3.
DATABASE_USER = 'knesset'      # Not used with sqlite3.
DATABASE_PASSWORD = '123456'      # Not used with sqlite3.
DATABASE_HOST = ''                  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                  # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'he'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_ROOT = os.path.join(PROJECT_ROOT, 'data')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/django_admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1_ovxxkf(c*z_dwv!(-=dezf#%l(po5%#zzi*su-$d*_j*1sr+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'openid_consumer.middleware.OpenIDMiddleware',
    # make sure to keep the DebugToolbarMiddleware last
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'knesset.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
    
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'piston',
    'debug_toolbar',
    'knesset',
    'knesset.mks',
    'knesset.laws',
    'knesset.simple',
    'socialauth',
    'openid_consumer',
    'tagging',
    'knesset.tagvotes',
    'django.contrib.comments',
    'knesset.accounts',
)
TEMPLATE_CONTEXT_PROCESSORS = (
"django.core.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.request",
"knesset.context.processor",
)
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


if hostname == 'ofri-laptop': # just an example of host-specific definitions. use if nessecery
    DATABASE_USER = 'knesset'     
    DATABASE_PASSWORD = '123456'  

OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_SREG = {"requred": "nickname, email", "optional":"postcode, country", "policy_url": ""}

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''


FACEBOOK_API_KEY = 'e7698d234fef3813756578fa4b927917'
FACEBOOK_API_SECRET = 'd765c75c355a90c31090420e546cb83a'


AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'socialauth.auth_backends.OpenIdBackend',
                           'socialauth.auth_backends.FacebookBackend',
                           )
#print "PATH: %s" % sys.path

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SITE_NAME = 'Open-Knesset'
