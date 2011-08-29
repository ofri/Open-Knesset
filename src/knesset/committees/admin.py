from knesset.committees.models import *

from django.contrib import admin

class CommitteeAdmin(admin.ModelAdmin):
    ordering = ('name',)
admin.site.register(Committee, CommitteeAdmin)

class CommitteeMeetingAdmin(admin.ModelAdmin):
    ordering = ('-date',)
admin.site.register(CommitteeMeeting, CommitteeMeetingAdmin)
