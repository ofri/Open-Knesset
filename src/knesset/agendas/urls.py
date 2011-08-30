#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from models import *
from views import *

agenda_list_view            = AgendaListView(queryset = Agenda.objects.all(),paginate_by=0, extra_context={'title':ugettext('Agendas')})
agenda_detail_view          = AgendaDetailView.as_view()
agenda_mk_detail_view       = AgendaMkDetailView.as_view()
agenda_detail_edit_view     = AgendaDetailEditView.as_view()


urlpatterns = patterns('',
    url(r'^$', agenda_list_view, name='agenda-list'),
    url(r'^(?P<pk>\d+)/$', agenda_detail_view, name='agenda-detail'),
    url(r'^(?P<pk>\d+)/member/(?P<member_id>\d+)/$', agenda_mk_detail_view, name='mk-agenda-detail'),
    url(r'^(?P<pk>\d+)/edit/$', agenda_detail_edit_view, name='agenda-detail-edit'),
    url(r'^add/$', agenda_add_view, name='agenda-add'),
    url(r'^update/votes/$', update_editors_agendas, name='update-editors-agendas'),
#    url(r'^user/(?P<user_id>\d+)/$', user_agendas_list_view, name),
#    url(r'^vote/(?P<vote_id>\d+)/$', ascribe_agenda_to_vote),
)
