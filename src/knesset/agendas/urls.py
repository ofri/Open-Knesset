#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from models import *
from views import *

agenda_list_view = AgendaListView(queryset = Agenda.objects.all(),paginate_by=20, extra_context={'title':ugettext('Agendas')})
agenda_detail_view = AgendaDetailView(queryset = Agenda.objects.all())


urlpatterns = patterns('',
    url(r'^$', agenda_list_view, name='agenda-list'),
    url(r'^(?P<object_id>\d+)/$', agenda_detail_view, name='agenda-detail'),
)
