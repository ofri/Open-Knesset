from knesset.topics.models import *

from django.contrib import admin

class TopicAdmin(admin.ModelAdmin):
    pass

admin.site.register(Topic, TopicAdmin)



