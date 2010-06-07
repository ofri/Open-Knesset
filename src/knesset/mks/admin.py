from django import forms
from django.contrib import admin
from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes import generic

from knesset.mks.models import *
from knesset.links.models import Link


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    
class MemberLinksInline(generic.GenericTabularInline):
    model = Link
    ct_fk_field = 'object_pk'
    extra = 1


class PartyAdmin(admin.ModelAdmin):
    ordering = ('name',)
#    fields = ('name','start_date','end_date', 'is_coalition','number_of_members')
    list_display = ('name','start_date', 'end_date','is_coalition', 'number_of_members', 'number_of_seats')
    inlines = (MembershipInline,)

admin.site.register(Party, PartyAdmin)

class MemberAdmin(admin.ModelAdmin):
    ordering = ('name',)
#    fields = ('name','start_date','end_date')
    list_display = ('name','PartiesString', 'TotalVotesCount','ForVotesCount', 'AgainstVotesCount','AbstainVotesCount')
    inlines = (MembershipInline, MemberLinksInline)

    # A template for a very customized change view:
    change_form_template = 'admin/simple/change_form_with_extra.html'

    
    def change_view(self, request, object_id, extra_context=None):
        m = Member.objects.get(id=object_id)
        my_context = {
            'extra': {'hi_corr':m.CorrelationListToString(m.HighestCorrelations()),
                      'low_corr':m.CorrelationListToString(m.LowestCorrelations()),
                      }
        }
        return super(MemberAdmin, self).change_view(request, object_id,
            extra_context=my_context)
admin.site.register(Member, MemberAdmin)

class CorrelationAdmin(admin.ModelAdmin):
    ordering = ('-normalized_score',)
admin.site.register(Correlation, CorrelationAdmin)

class MembershipAdmin(admin.ModelAdmin):
    ordering = ('member__name',)
admin.site.register(Membership, MembershipAdmin)
