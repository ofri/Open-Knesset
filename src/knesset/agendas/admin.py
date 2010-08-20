from knesset.agendas.models import *

from django.contrib import admin

class AgendaAdmin(admin.ModelAdmin):
    pass    
admin.site.register(Agenda, AgendaAdmin)

class AgendaVoteAdmin(admin.ModelAdmin):
    pass
admin.site.register(AgendaVote, AgendaVoteAdmin)

