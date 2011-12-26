from knesset.annotations.models import Annotation, AnnotationPermissions
from piston.handler import BaseHandler

class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Annotation
    csrf_exempt = True

    def create(self, request, *args, **kwargs):
      permission_data = request.data['permissions']
      permissions = AnnotationPermissions.objects.create(
          read = ','.join(permission_data['read']),
          update = ','.join(permission_data['update']),
          admin = ','.join(permission_data['admin']),
          delete = ','.join(permission_data['delete']))
      import pdb; pdb.set_trace()
      rc = BaseHandler.create(self, request, permissions_id = permissions.id, *args, **kwargs)
      return rc
