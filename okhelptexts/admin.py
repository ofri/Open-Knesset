from okhelptexts.models import Helptext,Keyword
from django.contrib import admin

class KeywordInline(admin.StackedInline):
    model = Keyword
    extra = 3

class HelptextAdmin(admin.ModelAdmin):
    inlines = [KeywordInline]

admin.site.register(Helptext,HelptextAdmin)