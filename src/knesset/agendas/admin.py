from knesset.agendas.models import *

from django.contrib import admin

class AgendaVoteInline(admin.TabularInline):
    model = AgendaVote
    extra = 1

class AgendaAdmin(admin.ModelAdmin):
#    inlines = (AgendaVoteInline, )
    pass
admin.site.register(Agenda, AgendaAdmin)

#class AgendaVoteAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(AgendaVote, AgendaVoteAdmin)

