from knesset.laws.models import *

from django import forms
from django.contrib import admin
from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory

class VoteAdmin(admin.ModelAdmin):
#    filter_horizontal = ('voted_for','voted_against','voted_abstain','didnt_vote')
    list_display =  ('__unicode__','short_summary','full_text_link','for_votes_count','against_votes_count')
admin.site.register(Vote, VoteAdmin)

class LawAdmin(admin.ModelAdmin):
    pass
admin.site.register(Law, LawAdmin)

class PrivateProposalAdmin(admin.ModelAdmin):
    pass
admin.site.register(PrivateProposal, PrivateProposalAdmin)

class KnessetProposalAdmin(admin.ModelAdmin):
    pass
admin.site.register(KnessetProposal, KnessetProposalAdmin)

