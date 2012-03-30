from datetime import datetime
from django.utils import simplejson
from piston.handler import BaseHandler
from piston.utils import rc
from knesset.annotations.models import Annotation, AnnotationPermissions

class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Annotation
    csrf_exempt = True

    # Sample curl call:
    # curl -d '{"permissions":{"read":["habeanf"],"update":["habeanf"],"delete":["habeanf"],"admin":["habeanf"]},"user":{"id":"habeanf","name":"habeanf"},"text":"oiuio","tags":[],"ranges":[{"start":"/div[3]/div[2]/blockquote/p","startOffset":4,"end":"/div[3]/div[2]/blockquote/p","endOffset":19}],"quote":"ÃÂ¨ Ãâ¢ÃÂ¨Ãâ¢Ãâ ÃÅÃâ¢Ãâ¢ÃÅ¸ - Ãâ","uri":"http://localhost:8000/committee/meeting/4163/"}' http://localhost:8000/annotation/ 
    def create(self, request, *args, **kwargs):
      if request.method != 'POST':
        return rc.ERROR
      print 1
      data = simplejson.loads(request.raw_post_data)
      print 2
      #data = simplejson.loads(request.POST.keys()[0])
      data.setdefault(None)
      permission_data = data['permissions']
      if permission_data:
          permissions = AnnotationPermissions.objects.create(
              read = permission_data['read'],
              update = permission_data['update'],
              admin =  permission_data['admin'],
              delete = permission_data['delete'])
      print 3
      #BaseHandler.create(
          #self, request, permissions_id = permissions.id, *args, **kwargs)
      annotation = Annotation.objects.create(
          annotator_schema_version = data.get('annotator_schema_version'),
          uri = data.get('uri'),
          account_id = data.get('account_id'),
          user = data.get('user'),
          text = data.get('text'),
          quote = data.get('quote'),
          created = data.get('created') or datetime.now(),
          ranges = data.get('ranges'),
          tags = data.get('tags'),
          permissions_id = permissions.id)
      print 4
      return rc.CREATED

