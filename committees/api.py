'''
Api for the committees app
'''
import tastypie.fields as fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from apis.resources.base import BaseResource
from models import Committee, CommitteeMeeting, ProtocolPart
from mks.api import MemberResource


class CommitteeResource(BaseResource):
    ''' Committee API
    '''
    recent_meetings = fields.ListField()
    future_meetings = fields.ListField()

    class Meta(BaseResource.Meta):
        queryset = Committee.objects.all()
        allowed_methods = ['get']
        include_absolute_url = True
        list_fields = ['description', 'name']
        filtering = {
            'id': ALL
        }

    def dehydrate_recent_meetings(self, bundle):
        return [
            {'url': x.get_absolute_url(), 'title': x.title(), 'date': x.date}
            for x in bundle.obj.recent_meetings()]

    def dehydrate_future_meetings(self, bundle):
        return [
            {'title': x.what, 'date': x.when}
            for x in bundle.obj.future_meetings()]


class CommitteeMeetingResource(BaseResource):
    ''' Committee Meeting API
    '''
    committee = fields.ForeignKey(CommitteeResource, 'committee')
    mks_attended = fields.ToManyField(MemberResource, 'mks_attended')
    protocol = fields.ToManyField('committees.api.ProtocolPartResource',
                                  'parts', full=True)

    class Meta(BaseResource.Meta):
        queryset = CommitteeMeeting.objects.select_related(
            'committee').prefetch_related('mks_attended')
        allowed_methods = ['get']
        include_absolute_url = True
        list_fields = ['committee', 'mks_attended', 'date', 'topics']
        excludes = ['protocol_text']
        filtering = {
            'date': ALL,
            'committee': ALL_WITH_RELATIONS
        }
        limit = 500


class ProtocolPartResource(BaseResource):
    header = fields.CharField(attribute='header')
    body = fields.CharField(attribute='body')

    class Meta(BaseResource.Meta):
        queryset = ProtocolPart.objects.all().order_by('order')
        allowed_methods = ['get']
        fields = list_fields = ['header', 'body']
        include_resource_uri = False
