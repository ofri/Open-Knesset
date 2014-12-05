from django.contrib import admin
from models import Lobbyist, LobbyistCorporation
from django.contrib.contenttypes import generic
from links.models import Link


class LinksInline(generic.GenericTabularInline):
    model = Link
    ct_fk_field = 'object_pk'
    extra = 1


class LobbyistAdmin(admin.ModelAdmin):
    inlines = (LinksInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('person', 'source_id',)
        return self.readonly_fields


class LobbyistCorporationAdmin(admin.ModelAdmin):
    inlines = (LinksInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'source_id',)
        return self.readonly_fields


admin.site.register(Lobbyist, LobbyistAdmin)
admin.site.register(LobbyistCorporation, LobbyistCorporationAdmin)

