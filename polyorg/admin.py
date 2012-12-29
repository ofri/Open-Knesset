from django.contrib import admin
from models import *


class MembershipInline(admin.TabularInline):
    model = CandidateList.candidates.through
    extra = 1

class CandidateListAdmin(admin.ModelAdmin):
    inlines = [MembershipInline,]
admin.site.register(CandidateList, CandidateListAdmin)
    
class CandidateAdmin(admin.ModelAdmin):
    pass
   
admin.site.register(Candidate, CandidateAdmin)

