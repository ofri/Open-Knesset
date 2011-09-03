from django.contrib.contenttypes.generic import GenericTabularInline
from knesset.committees.models import *

from django.contrib import admin

class CommitteeAdmin(admin.ModelAdmin):
    ordering = ('name',)
admin.site.register(Committee, CommitteeAdmin)

class CommitteeMeetingAdmin(admin.ModelAdmin):
    ordering = ('-date',)
admin.site.register(CommitteeMeeting, CommitteeMeetingAdmin)

class LinksTable(GenericTabularInline):
    model = Link
    ct_field='content_type'
    ct_fk_field='object_pk'

class EventsTable(GenericTabularInline):
    model = Event
    ct_field='which_type'
    ct_fk_field='which_pk'

class TopicAdmin(admin.ModelAdmin):
    ordering = ('-created',)
    inlines = [
        LinksTable,
        EventsTable,
    ]

admin.site.register(Topic, TopicAdmin)
