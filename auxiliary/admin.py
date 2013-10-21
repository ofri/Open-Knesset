from django.contrib import admin

from .models import Tidbit, TagSuggestion, Tag


def tags_suggestions_approve(modeladmin, request, queryset):
    "approve the suggestions"
    for ts in queryset:
        t=Tag(name = ts.name)
        t.save()
        ts.delete()



class TidibitAdmin(admin.ModelAdmin):

    model = Tidbit
    list_display = ('title', 'content', 'ordering', 'is_active')
    list_display_links = ('title', 'content')
    list_editable = ('ordering', 'is_active')


class TagSuggestionAdmin(admin.ModelAdmin):
    
    model = TagSuggestion
    list_display = ('name', 'suggested_by')
    actions = [tags_suggestions_approve]


admin.site.register(Tidbit, TidibitAdmin)
admin.site.register(TagSuggestion, TagSuggestionAdmin)
