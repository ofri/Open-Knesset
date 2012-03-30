from datetime import datetime
from django.utils import simplejson
from piston.handler import BaseHandler
from piston.utils import rc
from knesset.annotations.models import Annotation, AnnotationPermissions

class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Annotation
    csrf_exempt = True

    def create(self, request, *args, **kwargs):
      if request.method != 'POST':
        return rc.ERROR
      data = simplejson.loads(request.raw_post_data)
      data.setdefault(None)
      permission_data = data['permissions']
      if permission_data:
          permissions = AnnotationPermissions.objects.create(
              read = permission_data['read'],
              update = permission_data['update'],
              admin =  permission_data['admin'],
              delete = permission_data['delete'])

      BaseHandler.create(
          self, request, permissions_id = permissions.id, *args, **kwargs)
      #annotation = Annotation.objects.create(
          #annotator_schema_version = data.get('annotator_schema_version'),
          #uri = data.get('uri'),
          #account_id = data.get('account_id'),
          #user = data.get('user'),
          #text = data.get('text'),
          #quote = data.get('quote'),
          #created = data.get('created') or datetime.now(),
          #ranges = data.get('ranges'),
          #tags = data.get('tags'),
          #permissions_id = permissions.id)

      return rc.CREATED

