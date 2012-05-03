'''
API for the agendas app
'''
from django.contrib.auth.models import User
from tastypie.constants import ALL
import tastypie.fields as fields
from avatar.templatetags.avatar_tags import avatar_url

from knesset.api.resources.base import BaseResource
from mks.models import Member, Party
from agendas.models import Agenda, AgendaVote

class UserResource(BaseResource):
    class Meta(BaseResource.Meta):
        queryset = User.objects.all()
        include_absolute_url = True
        include_resource_uri = False
        allowed_methods = ['get']
        fields = ['username']

    avatar = fields.CharField()

    def dehydrate_avatar(self, bundle):
        return avatar_url(bundle.obj, 48)

class AgendaVoteResource(BaseResource):
    class Meta(BaseResource.Meta):
        object_class = AgendaVote
        allowed_methods = ['get']

    title = fields.CharField()

    def dehydrate_title(self, bundle):
        return bundle.obj.vote.title

class AgendaMKResource(BaseResource):
    class Meta(BaseResource.Meta):
        allowed_methods = ['get']
        resource_name = 'agenda/mk'

class AgendaResource(BaseResource):
    ''' Agenda API '''
    class Meta(BaseResource.Meta):
        queryset = Agenda.objects.filter(is_public=True)
        allowed_methods = ['get']
        include_absolute_url = True
        excludes = ['is_public']

    followers = fields.IntegerField(attribute="number_of_followers")
    editors = fields.ToManyField(UserResource,
                    'editors',
                    full=True)
    votes = fields.ToManyField(AgendaVoteResource,
                    'agendavotes',
                    full=True)

    def dehydrate(self, bundle):
        a = bundle.obj
        bundle.data['members'] = map(
                lambda x: dict(name=x.name, 
                    score = a.member_score(x),
                    absolute_url = x.get_absolute_url(),
                    party = x.current_party.name),
                Member.objects.all())
        bundle.data['parties'] = map(
                lambda x: dict(name=x.name, score=a.party_score(x),
                    absolute_url=x.get_absolute_url()),
                Party.objects.all())
        return bundle
