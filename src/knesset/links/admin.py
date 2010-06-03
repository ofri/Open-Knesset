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
           {'fields': ('url', 'title') }
        ),
     )

    list_display = ('title', 'content_type', 'object_pk')
    search_fields = ('title',)


admin.site.register(Link, LinksAdmin)
admin.site.register(LinkType, LinkTypesAdmin)
