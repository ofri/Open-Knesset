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
from models import Law, Bill, Vote

class LawResource(BaseResource):
    class Meta:
        queryset = Law.objects.all()
        allowed_methods = ['get']

class VoteResource(BaseResource):
    class Meta:
        queryset = Vote.objects.all()
        allowed_methods = ['get']

class BillResource(BaseResource):
    ''' Bill API '''
    class Meta:
        queryset = Bill.objects.all()
        allowed_methods = ['get']
        # excludes = ['stage']
        ordering = ['title', 'stage']
        filtering = dict(stage = ALL)

    proposers = fields.ToManyField(MemberResource,
                    'proposers',
                    full=True)
    pre_votes = fields.ToManyField(VoteResource,
                    'pre_votes',
                    null=True,
                    full=True)

    first_vote = fields.ToOneField(VoteResource,
                    'first_vote',
                    null=True,
                    full=True)

    approval_vote = fields.ToOneField(VoteResource,
                    'approval_vote',
                    null=True,
                    full=True)


    law = fields.ToOneField(LawResource, 'law', null=True, full=True)

    def dehydrate_stage(self, bundle):
        return bundle.obj.get_stage_display()

    def dehydrate(self, bundle):
        from simple.management.commands.syncdata import p_explanation
        bill = bundle.obj
        ps = bill.proposals.order_by('-date')[0]
        if ps.content_html:
            parts = ps.content_html.split(p_explanation)
            try:
                bundle.data.update(dict(legal_code = parts[0]+'</p>',
                    explanation = '<p>' + parts[1]))
            except IndexError:
                pass

        # bundle.data['stage'] = bill.get_stage_display()
        return bundle
