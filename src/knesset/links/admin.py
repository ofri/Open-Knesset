from django.contrib import admin
from models import *
from django.utils.translation import ugettext_lazy as _, ungettext

class LinkTypesAdmin(admin.ModelAdmin):
    pass

class LinksAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
           {'fields': ('content_type', 'object_pk')}
        ),
        (_('Content'),
           {'fields': ('url', 'title', 'link_type') }
        ),
     )

    list_display = ('title', 'link_type', 'content_type', 'object_pk')
    search_fields = ('title',)
    list_filter = ('link_type', )


admin.site.register(Link, LinksAdmin)
admin.site.register(LinkType, LinkTypesAdmin)
