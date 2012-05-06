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
        mks_values = dict(a.get_mks_values())
        members = []
        for mk in Member.objects.filter(pk__in = mks_values.keys()):
            # TODO: this sucks, performance wise
            current_party = mk.current_party
            members.append (dict(name=mk.name,
                    score = mks_values[mk.id]['score'],
                    rank = mks_values[mk.id]['rank'],
                    absolute_url = mk.get_absolute_url(),
                    party = current_party.name,
                    party_url = current_party.get_absolute_url(),
                ))
        bundle.data['members'] = members
        bundle.data['parties'] = map(
                lambda x: dict(name=x.name, score=a.party_score(x),
                    absolute_url=x.get_absolute_url()),
                Party.objects.all())
        return bundle

'''
class AgendaMKResource(Resource):
    class Meta(BaseResource.Meta):
        queryset = User.objects.all()
        include_absolute_url = True
        allowed_methods = ['get']
        resource_name = 'agenda/mk'

    def get_resource_uri(self, bundle_or_resource):
        kwargs = {'resource_name': self._meta.resource_name}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            # TODO: what goes here?
            pass

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def get_object_list(self):
        return "%(_uri_prefix)s/%(id)s/" % self

'''
