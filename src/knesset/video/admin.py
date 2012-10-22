from django.contrib import admin
from models import Video

class VideoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Video, VideoAdmin)
