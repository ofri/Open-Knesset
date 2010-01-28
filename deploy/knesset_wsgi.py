import os, sys, site
sys.stdout = sys.stderr

PROJECT_DIR='/home/daonb/sites/Open-Knesset/project'

syspath=[]
eggs_dir = os.path.join(PROJECT_DIR, 'eggs')
for part in os.listdir(eggs_dir):
	syspath.append(os.path.join(eggs_dir, part))
parts_dir = os.path.join(PROJECT_DIR, 'parts')
for part in os.listdir(parts_dir):
	syspath.append(os.path.join(parts_dir, part))
syspath.append(os.path.join(PROJECT_DIR, 'src'))
# sys.path.append(os.path.join(PROJECT_DIR, 'src', 'knesset'))
sys.path[0:0] = syspath
os.environ['DJANGO_SETTINGS_MODULE'] = 'knesset.settings_tuzig'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(PROJECT_DIR, 'eggs')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

