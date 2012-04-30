'''
API for the agendas app
'''
from tastypie.constants import ALL
import tastypie.fields as fields

from knesset.api.resources.base import BaseResource
from mks.models import Member, Party
from agendas.models import Agenda, AgendaVote

class AgendaVoteResource(BaseResource):
    class Meta(BaseResource.Meta):
        object_class = AgendaVote
        allowed_methods = ['get']

    title = fields.CharField()

    def dehydrate_title(self, bundle):
        return bundle.obj.vote.title

class MemberScoreResource(BaseResource):
    class Meta(BaseResource.Meta):
        object_class = Member
        allowed_methods = ['get']
        fields = ['score', 'name']

class PartyScoreResource(BaseResource):
    class Meta(BaseResource.Meta):
        object_class = Party
        allowed_methods = ['get']
        fields = ['score', 'name']

class AgendaResource(BaseResource):
    ''' Agenda API '''
    class Meta(BaseResource.Meta):
        queryset = Agenda.objects.filter(is_public=True)
        allowed_methods = ['get']
        # excludes = ['stage']
        filtering = dict(stage = ALL)
        include_absolute_url = True
        excludes = ['is_public']

    followers = fields.IntegerField(attribute="number_of_followers")
    explanation = fields.CharField()
    legal_code = fields.CharField()
    votes = fields.ToManyField(AgendaVoteResource,
                    'agendavotes',
                    full=True)
    def dehydrate(self, bundle):
        a = bundle.obj
        bundle.data['members'] = map(
                lambda x: dict(name=x.name, score=a.member_score(x),
                    absolute_url=x.get_absolute_url()),
                Member.objects.all())
        bundle.data['parties'] = map(
                lambda x: dict(name=x.name, score=a.party_score(x),
                    absolute_url=x.get_absolute_url()),
                Party.objects.all())
        return bundle
