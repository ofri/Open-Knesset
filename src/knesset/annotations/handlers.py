from knesset.annotations.models import Annotation
from piston.handler import BaseHandler

class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Annotation
