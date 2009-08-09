from knesset.simple.models import *

from django import forms
from django.contrib import admin
from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory


#class MemberInline(admin.StackedInline):
#    model = Member
#    formSet = inlineformset_factory(Party, Member, fields=() )
#
#    formset = formSet
    #list_editable = []

#class PartyAdmin(admin.ModelAdmin):
#    fields   = ('name', )
#    inlines  = [MemberInline,]

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1
    


class PartyAdmin(admin.ModelAdmin):
    ordering = ('name',)
    fields = ('name','start_date','end_date')
    list_display = ('name','start_date', 'end_date','MembersString')
    inlines = (MembershipInline,)

admin.site.register(Party, PartyAdmin)

class MemberAdmin(admin.ModelAdmin):
    ordering = ('name',)
    fields = ('name','start_date','end_date')
    list_display = ('name','PartiesString', 'TotalVotesCount','ForVotesCount', 'AgainstVotesCount','AbstainVotesCount')
    inlines = (MembershipInline,)

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
        
#class MemberAdmin(admin.ModelAdmin):
#    ordering = ('name',)
#    fields = ('name','start_date','end_date')
#    list_display = ('name','PartiesString', 'TotalVotesCount','ForVotesCount', 'AgainstVotesCount','AbstainVotesCount')
#    inlines = (MembershipInline,)


admin.site.register(Member, MemberAdmin)

class CorrelationAdmin(admin.ModelAdmin):
    ordering = ('-normalized_score',)
admin.site.register(Correlation, CorrelationAdmin)

class VoteAdmin(admin.ModelAdmin):
    filter_horizontal = ('voted_for','voted_against','voted_abstain','didnt_vote')
admin.site.register(Vote, VoteAdmin)

class MembershipAdmin(admin.ModelAdmin):
    ordering = ('member__name',)
admin.site.register(Membership, MembershipAdmin)

#