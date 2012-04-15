'''
Api for the members app
'''
from tastypie.constants import ALL
import tastypie.fields as fields

from mks.models import Member, Party
from knesset.api.resources.base import BaseResource
from video.utils import get_videos_queryset
from video.api import VideoResource

class PartyResource(BaseResource):
    ''' Party API
    TBD: create a party app
    '''

    class Meta:
        queryset = Party.objects.all()
        allowed_methods = ['get']

class MemberResource(BaseResource):
    ''' The Parliament Member API '''
    class Meta:
        queryset = Member.objects.all()
        allowed_methods = ['get']
        ordering = [
            'name',
            'is_current',
            'bills_stats_proposed',
            'bills_stats_pre',
            'bills_stats_first',
            'bills_stats_approved',
            ]
        filtering = dict(
            name = ALL,
            is_current = ALL,
            )
        exclude_from_list_view = ['about_video_id','related_videos_uri']

    party = fields.ToOneField(PartyResource, 'current_party')
    videos = fields.ToManyField(VideoResource,
                    attribute= lambda b: get_videos_queryset(b.obj),
                    null = True)

