# encoding: utf-8

from datetime import datetime
import json
from piston.handler import BaseHandler
from piston.utils import rc
from knesset.annotations.models import Annotation, AnnotationPermissions

class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Annotation
    csrf_exempt = True

    # Sample curl call:
    # curl -d '{"permissions":{"read":["habeanf"],"update":["habeanf"],"delete":["habeanf"],"admin":["habeanf"]},"user":{"id":"habeanf","name":"habeanf"},"text":"oiuio","tags":[],"ranges":[{"start":"/div[3]/div[2]/blockquote/p","startOffset":4,"end":"/div[3]/div[2]/blockquote/p","endOffset":19}],"quote":"ÃÂ¨ Ãâ¢ÃÂ¨Ãâ¢Ãâ ÃÅÃâ¢Ãâ¢ÃÅ¸ - Ãâ","uri":"http://localhost:8000/committee/meeting/4163/"}' http://localhost:8000/annotation/ --header="Content-Type: application/json"
    def create(self, request, *args, **kwargs):
      if request.method != 'POST':
        return rc.ERROR
      #data.setdefault(None)
      data = request.data
      import pdb; pdb.set_trace()
      #data = simplejson.loads(request.POST.keys()[0])
      permission_data = data['permissions']
      if permission_data:
          permissions = AnnotationPermissions.objects.create(
              read = permission_data['read'],
              update = permission_data['update'],
              admin =  permission_data['admin'],
              delete = permission_data['delete'])
      item = self.model(
          annotator_schema_version = data['annotator_schema_version'],
          uri = data['uri'],
          account_id = data['account_id'],
          user = data['user'],
          text = data['text'],
          quote = data['quote'],
          created = data['created'] or datetime.now(),
          ranges = data['ranges'],
          tags = data['tags'],
          permissions_id = permissions.id)
      item.save()
      return rc.CREATED

