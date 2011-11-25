from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('video/_video_init.html')
def video_init():
    return {
        'MEDIA_URL':settings.MEDIA_URL
    }

@register.inclusion_tag('video/_video_player.html')
def video_player(width,height,embed_link,image_link):
    embed_link=embed_link if embed_link is not None else ''
    image_link=image_link if image_link is not None else ''
    return {
        'width':width, 'height':height,
        'embed_link':embed_link,
        'image_link':image_link,
    }
