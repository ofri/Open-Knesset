from django.contrib import admin
from models import Person,PersonAlias,Title,Role

class RoleInline(admin.TabularInline):
    model = Role

class PersonAdmin(admin.ModelAdmin):
    list_display=('name', 'mk', 'user')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [
        RoleInline,
    ]
    readonly_fields = ('calendar_sync_token',)

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
