from knesset.video.models import Video
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Video, VideoAdmin)
