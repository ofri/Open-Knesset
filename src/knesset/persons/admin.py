from knesset.persons.models import Person,PersonAlias,Title,Role

from django.contrib import admin


class RoleInline(admin.TabularInline):
    model = Role

class PersonAdmin(admin.ModelAdmin):
    ordering = ('name',)
    inlines = [
        RoleInline,
    ]

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
