from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.hashnav import ListView, DetailView
from models import Person
from views import PersonListView,PersonDetailView

person_list = ListView(queryset = Person.objects.filter(protocol_parts__isnull=False).distinct(),paginate_by=50)
person_detail = PersonDetailView(queryset = Person.objects.all())

urlpatterns = patterns ('',
    url(r'^$', person_list, name='person-list'),
    url(r'^(?P<object_id>\d+)/$', person_detail, name='person-detail'),
)
