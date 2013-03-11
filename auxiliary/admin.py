from django.contrib import admin

from .models import Tidbit


class TidibitAdmin(admin.ModelAdmin):

    model = Tidbit
    list_display = ('title', 'content', 'ordering', 'is_active')
    list_display_links = ('title', 'content')
    list_editable = ('ordering', 'is_active')


admin.site.register(Tidbit, TidibitAdmin)
