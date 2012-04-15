'''
Api for the members app
'''
from tastypie.resources import ModelResource
from tastypie.constants import ALL
import tastypie.fields as fields

from mks.models import Member, Party
from knesset.api.resources.base import BaseResource
from video.utils import get_videos_queryset

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

    current_party_id = fields.IntegerField(readonly=True)
    about_video_id = fields.IntegerField(readonly=True)

    def dehydrate_current_party_id(self,bundle):
        return bundle.obj.current_party.id

    def dehydrate_about_video_id(self,bundle):
        about_videos=get_videos_queryset(bundle.obj,group='about')
        if about_videos.count()>0:
            return about_videos[0].id
        else:
            return None

class PartyResource(BaseResource):
    ''' Party API
    TBD: create a party app
    '''

    class Meta:
        queryset = Party.objects.all()
        allowed_methods = ['get']
