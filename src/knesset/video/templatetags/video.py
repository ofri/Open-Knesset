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
    
@register.inclusion_tag('video/_video_playlist.html')
def video_playlist(videos):
    return {'videos':videos}
   
@register.inclusion_tag('video/_video_playlist_player.html')
def video_playlist_player(video):
    return {
        'embed_link':video.embed_link,
        'image_link':video.small_image_link,
        'title':video.title,
        'description':video.description,
        'link':video.link,
        'published':video.published,
    }

