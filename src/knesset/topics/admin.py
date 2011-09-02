from knesset.topics.models import *
from django.contrib.contenttypes.generic import GenericTabularInline

from django.contrib import admin


class LinksTable(GenericTabularInline):
    model = Link
    ct_field='content_type'
    ct_fk_field='object_pk'

class EventsTable(GenericTabularInline):
    model = Event
    ct_field='which_type'
    ct_fk_field='which_pk'

class TopicAdmin(admin.ModelAdmin):
    inlines = [
        LinksTable,
        EventsTable,
    ]

admin.site.register(Topic, TopicAdmin)



