# Django settings for knesset project.
import os
import logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'django.db.backends.sqlite3'         # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'dev.db'  # Or path to database file if using sqlite3.
DATABASE_USER = ''      # Not used with sqlite3.
DATABASE_PASSWORD = ''      # Not used with sqlite3.
DATABASE_HOST = ''                  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                  # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Jerusalem'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'he'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DATA_ROOT = os.path.join(PROJECT_ROOT, os.path.pardir,os.path.pardir,'data','')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, os.path.pardir,os.path.pardir,'static', ''))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

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
    'django.middleware.csrf.CsrfViewMiddleware',    
    'pagination.middleware.PaginationMiddleware',
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
    'django.contrib.auth',          # django apps
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.sitemaps',
    'piston',                       # friends apps
    'debug_toolbar',
    'tagging',
    'haystack',
    'south',
    'planet',
    'pagination',
    'django_extensions',
    'actstream',
    'gravatar',
    'annotatetext',
    'knesset.auxiliary',                  # knesset apps
    'knesset.mks',
    'knesset.laws',
    'knesset.committees',
    'knesset.simple',
    'knesset.tagvotes',
    'knesset.accounts',
    'knesset.links',
    'knesset.user',
    'knesset.badges',
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
# Add the following line to your local_settings.py files to disable django-debug-toolar:
#INTERNAL_IPS = ()
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

LOCAL_DEV = True

LOGIN_URL = '/user/login/'

SITE_NAME = 'Open-Knesset'
HAYSTACK_SITECONF = 'knesset.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'whoosh_index')
HAYSTACK_INCLUDE_SPELLING = True


MAX_TAG_LENGTH = 128

AUTH_PROFILE_MODULE = 'user.UserProfile'

LOGIN_REDIRECT_URL = '/'

USER_AGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)"

LOG_FILENAME = os.path.join(PROJECT_ROOT, 'open-knesset.log')
logger = logging.getLogger("open-knesset")
logger.setLevel(logging.DEBUG)  # override this in prod server to logging.ERROR
h = logging.FileHandler(LOG_FILENAME)
h.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")
h.setFormatter(formatter)
logger.addHandler(h)

GOOGLE_MAPS_API_KEYS = {'dev': 'ABQIAAAAWCfW8hHVwzZc12qTG0qLEhQCULP4XOMyhPd8d_NrQQEO8sT8XBQdS2fOURLgU1OkrUWJE1ji1lJ-3w',
                        'prod': 'ABQIAAAAWCfW8hHVwzZc12qTG0qLEhR8lgcBs8YFes75W3FA_wpyzLVCpRTF-eaJoRuCHAJ2qzVu-Arahwp8QA'}
GOOGLE_MAPS_API_KEY = GOOGLE_MAPS_API_KEYS['dev'] # override this in prod server

CACHE_BACKEND = 'dummy://'


# if you add a local_settings.py file, it will override settings here
# but please, don't commit it to git.
try: 
    from local_settings import *
except ImportError:
    pass