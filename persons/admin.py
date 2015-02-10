from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from links.models import Link
from models import Person,PersonAlias,Title,Role, ExternalInfo, ExternalRelation

class RoleInline(admin.TabularInline):
    model = Role

class ExternalInfoInline(admin.TabularInline):
    model = ExternalInfo
    extra = 1

class ExternalRelationInline(admin.TabularInline):
    model = ExternalRelation
    fk_name = 'person'
    extra = 1

def merge_persons(modeladmin, request, qs):
    pivot = None
    for person in qs:
        if person.mk:
            pivot = person
            break
    if not pivot:
        # if no mk based pivot, pick the first one
        pivot = qs[0]
    else:
        # copy the mks' roles and links to person
        #TODO: code the next method
        #person.copy(mk=mk)
        pass

    for person in qs:
        if person != pivot:
            pivot.merge(person)

merge_persons.short_description = _("Merge two or more persons")

class PersonAdmin(admin.ModelAdmin):
    list_display=('name', 'mk', 'user')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [ RoleInline, ExternalInfoInline, ExternalRelationInline ]
    readonly_fields = ('calendar_sync_token',)
    actions = [merge_persons]

admin.site.register(Person, PersonAdmin)

class PersonAliasAdmin(admin.ModelAdmin):
    ordering = ('person',)
    list_display = ('person','name')
admin.site.register(PersonAlias, PersonAliasAdmin)

class TitleAdmin(admin.ModelAdmin):
    ordering = ('name',)
admin.site.register(Title, TitleAdmin)

class RoleAdmin(admin.ModelAdmin):
    ordering = ('person',)
    list_display = ('person','text')
admin.site.register(Role, RoleAdmin)

