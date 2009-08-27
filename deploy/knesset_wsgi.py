import os, sys, site

PROJECT_DIR='/home/daonb/sites/Open-Knesset/project'

# site.addsitedir(os.path.join(PROJECT_DIR, 'parts'))
sys.path.append(os.path.join(PROJECT_DIR, 'parts', 'django'))
sys.path.append(os.path.join(PROJECT_DIR, 'parts', 'piston'))
sys.path.append(os.path.join(PROJECT_DIR, 'src'))
sys.path.append(os.path.join(PROJECT_DIR, 'src', 'knesset'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'runsettings'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(PROJECT_DIR, 'eggs')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

