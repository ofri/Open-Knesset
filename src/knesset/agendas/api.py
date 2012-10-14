'''
API for the agendas app
'''
from django.contrib.auth.models import User
from tastypie.constants import ALL
import tastypie.fields as fields
from avatar.templatetags.avatar_tags import avatar_url

from knesset.api.resources.base import BaseResource
from knesset.mks.models import Member, Party
from knesset.agendas.models import Agenda, AgendaVote

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
        queryset = AgendaVote.objects.select_related()
        allowed_methods = ['get']

    title = fields.CharField()

    def dehydrate_title(self, bundle):
        return bundle.obj.vote.title

class AgendaTodoResource(BaseResource):
    class Meta(BaseResource.Meta):
        allowed_methods = ['get']
        queryset = Agenda.objects.all()
        resource_name = 'agenda-todo'
        fields = ['votes_by_conrtoversy', 'votes_by_agendas']

    votes_by_controversy = fields.ListField()
    votes_by_agendas = fields.ListField()

    # TODO: Make this a parameter or setting or something
    NUM_SUGGESTIONS = 10

    def dehydrate_votes_by_agendas(self, bundle):
        votes = bundle.obj.get_suggested_votes_by_agendas(AgendaTodoResource.NUM_SUGGESTIONS)
        return self._dehydrate_votes(votes)

    def dehydrate_votes_by_controversy(self, bundle):
        votes = bundle.obj.get_suggested_votes_by_controversy(AgendaTodoResource.NUM_SUGGESTIONS)
        return self._dehydrate_votes(votes)

    def _dehydrate_votes(self, votes):
        def dehydrate_vote(vote):
            return dict(id=vote.id,
                        url=vote.get_absolute_url(),
                        title=vote.title,
                        score=vote.score)
        return [dehydrate_vote(v) for v in votes]


class AgendaResource(BaseResource):
    ''' Agenda API '''
    class Meta(BaseResource.Meta):
        queryset = Agenda.objects.filter(is_public=True).prefetch_related('agendavotes__vote', 'editors')
        allowed_methods = ['get']
        include_absolute_url = True
        excludes = ['is_public']
        list_fields = ['name', 'id', 'description', 'public_owner_name']
    #editors = fields.ToManyField(UserResource,
    #                'editors',
    #                full=True)
    #votes = fields.ToManyField(AgendaVoteResource,
    #                'agendavotes',
    #                full=True)

    def dehydrate(self, bundle):
        a = bundle.obj
        if self.get_resource_uri(bundle) == bundle.request.path:
            # it's a detailed request so we add the mks & parties scores
            mks_values = dict(a.get_mks_values())
            members = []
            for mk in Member.objects.filter(pk__in=mks_values.keys()).select_related('current_party'):
                # TODO: this sucks, performance wise
                current_party = mk.current_party
                members.append (dict(name=mk.name,
                        score = mks_values[mk.id]['score'],
                        rank = mks_values[mk.id]['rank'],
                        volume = mks_values[mk.id]['volume'],
                        absolute_url = mk.get_absolute_url(),
                        party = current_party.name,
                        party_url = current_party.get_absolute_url(),
                    ))
            bundle.data['members'] = members
            bundle.data['parties'] = [
                dict(
                    name=x.name, score=a.party_score(x),
                    absolute_url=x.get_absolute_url()
                ) for x in Party.objects.prefetch_related('members')
            ]
            bundle.data['votes'] = [
                dict(title=v.vote.title, id=v.id, importance=v.importance,
                     score=v.score, reasoning=v.reasoning)
                for v in bundle.obj.agendavotes.select_related()
            ]


        bundle.data['editors'] = [
            dict(absolute_url=e.get_absolute_url(), username=e.username,
                 avatar=avatar_url(e, 48))
            for e in bundle.obj.editors.all()]

        return bundle
