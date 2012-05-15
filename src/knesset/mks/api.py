'''
Api for the members app
'''
from tastypie.constants import ALL
import tastypie.fields as fields

from knesset.api.resources.base import BaseResource
from mks.models import Member, Party
from agendas.models import Agenda
from video.utils import get_videos_queryset
from video.api import VideoResource
from links.models import Link
from links.api import LinkResource

class PartyResource(BaseResource):
    ''' Party API
    TBD: create a party app
    '''

    class Meta:
        queryset = Party.objects.all()
        allowed_methods = ['get']
        excludes = ['end_date', 'start_date']
        include_absolute_url = True

class MemberAgendasResource(BaseResource):
    ''' The Parliament Member Agenda-compliance API '''
    class Meta:
        queryset = Member.objects.all()
        allowed_methods = ['get']
        fields = ['agendas'] # We're not really interested in any member details here
        resource_name = "member-agendas"

    def dehydrate(self, bundle):
        mk = bundle.obj
        agendas_values = mk.get_agendas_values()
        friends = mk.current_party.current_members().values_list('id', flat=True)
        agendas = []
        for a in Agenda.objects.filter(pk__in = agendas_values.keys(),
                is_public = True):
            amin = 200.0 ; amax = -200.0
            pmin = 200.0 ; pmax = -200.0
            av = agendas_values[a.id]
            for mk_id, values in a.get_mks_values():
                score = values['score']
                if score < amin:
                    amin = score
                if score > amax:
                    amax = score
                if mk_id in friends:
                    if score < pmin:
                        pmin = score
                    if score > pmax:
                        pmax = score

            agendas.append(dict(name = a.name,
                id = a.id,
                owner = a.public_owner_name,
                score = av['score'],
                rank = av['rank'],
                min = amin,
                max = amax,
                party_min = pmin,
                party_max = pmax,
                absolute_url = a.get_absolute_url(),
                ))
        bundle.data['agendas'] = agendas
        return bundle

class MemberResource(BaseResource):
    ''' The Parliament Member API '''
    class Meta:
        queryset = Member.objects.all().select_related('current_party')
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
        exclude_from_list_view = ['about_video_id','related_videos_uri',
                'links', 'videos']
        excludes = ['website', 'backlinks_enabled', 'area_of_residence']

    party = fields.ToOneField(PartyResource, 'current_party', full=True)
    videos = fields.ToManyField(VideoResource,
                    attribute= lambda b: get_videos_queryset(b.obj),
                    null = True)
    links = fields.ToManyField(LinkResource,
                    attribute = lambda b: Link.objects.for_model(b.obj),
                    full = True,
                    null = True)

    def dehydrate_gender(self, bundle):
        return bundle.obj.get_gender_display()

    def dehydrate(self, bundle):
        bundle.data['agendas_uri'] = MemberAgendasResource().get_resource_uri(bundle)
        return bundle

