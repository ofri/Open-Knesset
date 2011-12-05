#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from models import *
from views import *

urlpatterns = patterns('',
    url(r'^$', Annotation.as_view(action="create")),
    url(r'^annotations/(?P<id>))?/$', Annotation.as_view(action="read_update_destroy")),
    url(r'search?/$', Annotation.as_view(action="search"))
)
