from django.conf import settings

TEMPLATES_INCLUDE_DIR = getattr(settings, 'TEMPLATES_INCLUDE_DIR', 'include')

