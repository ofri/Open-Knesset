'''
API for the laws app
'''
from tastypie.constants import ALL
import tastypie.fields as fields

from knesset.api.resources.base import BaseResource
from mks.models import Member, Party
from mks.api import MemberResource
from video.utils import get_videos_queryset
from video.api import VideoResource
from links.models import Link
from links.api import LinkResource

class LawResource(BaseResource):
    class Meta:
        queryset = Law.objects.all()
        allowed_methods = ['get']

class BillResource(BaseResource):
    ''' Bill API '''

    class Meta:
        queryset = Bill.objects.all()
        allowed_methods = ['get']
        ordering = [
            'title',
            'stage',
        ]
        filtering = dict(
            stage = ALL,
            )
    proposers = fields.ToManyField(MemberResource,
                    'proposers',
                )



    law = fields.ToOneField(LawResource, 'law', full=True)

