from django.contrib.contenttypes.generic import GenericTabularInline
from knesset.committees.models import *
from knesset.video.models import Video
from django.db.models import Q

from django.contrib import admin

class CommitteeRelatedVideosInline(generic.GenericTabularInline):
    model = Video
    ct_fk_field = 'object_pk'
    can_delete = False
    fields = ['title','description','embed_link','group','hide']
    ordering = ['group','-published']
    readonly_fields = ['title','description','embed_link','group']
    extra = 0
    def queryset(self, request):
        qs = super(CommitteeRelatedVideosInline, self).queryset(request)
        qs = qs.filter(Q(hide=False) | Q(hide=None))
        return qs

class EventsTable(GenericTabularInline):
    model = Event
    ct_field='which_type'
    ct_fk_field='which_pk'

class CommitteeAdmin(admin.ModelAdmin):
    ordering = ('name',)
    inlines = (CommitteeRelatedVideosInline, EventsTable)
admin.site.register(Committee, CommitteeAdmin)

class CommitteeMeetingAdmin(admin.ModelAdmin):
    ordering = ('-date',)
admin.site.register(CommitteeMeeting, CommitteeMeetingAdmin)

class LinksTable(GenericTabularInline):
    model = Link
    ct_field='content_type'
    ct_fk_field='object_pk'


class TopicAdmin(admin.ModelAdmin):
    ordering = ('-created',)
    inlines = [
        LinksTable,
        EventsTable,
    ]

admin.site.register(Topic, TopicAdmin)
