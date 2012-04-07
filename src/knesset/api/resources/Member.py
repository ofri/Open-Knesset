from tastypie.resources import ModelResource
from tastypie.constants import ALL
import tastypie.fields as fields
from django.db.models import Q
from knesset.mks.models import Member


class MemberResource(ModelResource):
    role = fields.CharField(readonly=True)
    current_party_id = fields.IntegerField(readonly=True)
    average_weekly_presence = fields.FloatField(readonly=True)
    committee_meetings_per_month = fields.IntegerField(readonly=True)
    num_bills = fields.DictField(readonly=True)
    average_votes_per_month = fields.FloatField(readonly=True)
    
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
            
            # the old view supported sorting by the following fields as well
            # but they are custom fields and tastypie does not support ordering by them
            # we can override, maybe the ModelResource.apply_sorting method
            # but this requires fetching ALL the rows and is very inefficient
            #    'average_votes_per_month',
            #    'average_weekly_presence',
            #    'committee_meetings_per_month',
            ]
        filtering= {
            'name': ALL,
            'is_current': ALL,
            }
    
    def dehydrate_role(self, bundle):
        return bundle.obj.get_role
    
    def dehydrate_current_party_id(self, bundle):
        return bundle.obj.current_party.id
    def dehydrate_average_weekly_presence(self, bundle):
        return bundle.obj.average_weekly_presence()
    def dehydrate_committee_meetings_per_month(self, bundle):
        return bundle.obj.committee_meetings_per_month()
    def dehydrate_num_bills(self, bundle):
        return dict(
            proposed=bundle.obj.bills.count(),
            pre=bundle.obj.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
            first=bundle.obj.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
            approved=bundle.obj.bills.filter(stage='6').count(),
        )
    def dehydrate_average_votes_per_month(self, bundle):
        return bundle.obj.voting_statistics.average_votes_per_month(),
    
    
    
    
    
    
    
    
        