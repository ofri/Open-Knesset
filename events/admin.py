from django.contrib import admin
from django.contrib.contenttypes import generic

from links.models import Link
from models import Event


class EventLinksInline(generic.GenericTabularInline):

    model = Link
    ct_fk_field = 'object_pk'
    extra = 1


class EventAdmin(admin.ModelAdmin):

    ordering = ('when',)
    list_display = ('when', 'what', 'where')
    inlines = (EventLinksInline,)
    date_hierarchy = 'when'


admin.site.register(Event, EventAdmin)
