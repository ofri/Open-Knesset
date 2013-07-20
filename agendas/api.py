'''
API for the agendas app
'''
from django.utils.timezone import datetime

import tastypie.fields as fields
from avatar.templatetags.avatar_tags import avatar_url
from django.contrib.auth.models import User

from models import Agenda, AgendaVote
from apis.resources.base import BaseResource
from mks.models import Member, Party

from operator import itemgetter

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
        votes = bundle.obj.get_suggested_votes_by_agendas(
            AgendaTodoResource.NUM_SUGGESTIONS)
        return self._dehydrate_votes(votes)

    def dehydrate_votes_by_controversy(self, bundle):
        votes = bundle.obj.get_suggested_votes_by_controversy(
            AgendaTodoResource.NUM_SUGGESTIONS)
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

    members = fields.ListField()
    parties = fields.ListField()
    votes = fields.ListField()
    editors = fields.ListField()
    ranges = fields.ListField()

    class Meta(BaseResource.Meta):
        queryset = Agenda.objects.filter(
            is_public=True).prefetch_related('agendavotes__vote', 'editors')
        allowed_methods = ['get']
        include_absolute_url = True
        excludes = ['is_public']
        list_fields = ['name', 'id', 'description', 'public_owner_name']

    def dehydrate_members(self, bundle):
        rangesString = bundle.request.GET.get('ranges',None)
        fullRange = rangesString is None
        if not fullRange:
            ranges = map(   lambda rangeString:[datetime.strptime(val,"%Y%m") if val else None for val in rangeString.split('-')],
                            rangesString.split(','))
            mks_values = dict(bundle.obj.get_mks_values(ranges))
        else:
            mks_values = dict(bundle.obj.get_mks_values())
        members = []
        for mk in Member.objects.filter(pk__in=mks_values.keys(),
                                        current_party__isnull=False).select_related('current_party'):
            # TODO: this sucks, performance wise
            current_party = mk.current_party
            mk_data = mks_values[mk.id]
            members.append(dict(
                id=mk.id,
                name=mk.name,
                score=map(itemgetter('score'),mk_data) if isinstance(mk_data,list) else mk_data['score'],
                rank=map(itemgetter('rank'),mk_data) if isinstance(mk_data,list) else mk_data['rank'],
                volume=map(itemgetter('volume'),mk_data) if isinstance(mk_data,list) else mk_data['volume'],
                numvotes=map(itemgetter('numvotes'),mk_data) if isinstance(mk_data,list) else mk_data['numvotes'],
                absolute_url=mk.get_absolute_url(),
                party=current_party.name,
                party_url=current_party.get_absolute_url(),
                party_id=current_party.pk
            ))

        return members

    def dehydrate_parties(self, bundle):
        party_values = dict(map(lambda party_data:(party_data[0],(party_data[1],party_data[2])),
                            bundle.obj.get_party_values()))
        parties = []
        for party in Party.objects.all():
            if party.pk in party_values:
                parties.append(dict(name=party.name, 
                                    score=party_values[party.pk][0], 
                                    volume=party_values[party.pk][1],
                                    absolute_url=party.get_absolute_url()))
            else:
                parties.append(dict(name=party.name,
                                    score=0,
                                    volume=0,
                                    absolute_url=party.get_absolute_url()))
        return parties

    def dehydrate_votes(self, bundle):
        return [
            dict(title=v.vote.title, id=v.vote_id, importance=v.importance,
                 score=v.score, reasoning=v.reasoning)
            for v in bundle.obj.agendavotes.select_related()
        ]

    def dehydrate_editors(self, bundle):
        return [
            dict(absolute_url=e.get_absolute_url(), username=e.username,
                 avatar=avatar_url(e, 48))
            for e in bundle.obj.editors.all()
        ]

    def dehydrate_ranges(self, bundle):
        rangesString = bundle.request.GET.get('ranges','-')
        ranges = map(   lambda rangeString:[int(val) if val else None for val in rangeString.split('-')],
                        rangesString.split(','))
        results = []
        for start,end in ranges:
            rangeResult = {}
            if start:
                rangeResult['from']=datetime(year=start/100,month=start%100,day=1)
            if end:
                rangeResult['to']=datetime(year=end/100,month=end%100,day=1)
            results.append(rangeResult)
        return results
