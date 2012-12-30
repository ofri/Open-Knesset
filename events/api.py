'''
Api for the events app
'''
import datetime
from models import Event
from tastypie.utils import trailing_slash
from apis.resources.base import BaseResource
from django.conf.urls.defaults import url

class EventResource(BaseResource):
    class Meta:
        queryset = Event.objects.all()
        allowed_methods = ['get']

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/?' % self._meta.resource_name,
                self.wrap_view('get_future_events'),
                name = 'api-get-future-events')
        ]

    def get_future_events(self, request, **kwargs):
        events = Event.objects.filter(when__gte = datetime.datetime.now())
        bundles = [self.build_bundle(obj = event, request = request) for event in events]
        return self.create_response(request, map(self.full_dehydrate, bundles))
