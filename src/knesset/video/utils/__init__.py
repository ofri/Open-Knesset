# encoding: utf-8

from django.contrib.contenttypes.models import ContentType
from knesset.video.models import Video
from django.db.models import Q
import urllib

def get_videos_queryset(obj,group=None):
    object_type=ContentType.objects.get_for_model(obj)
    filterKwargs={
        'content_type__pk':object_type.id,
        'object_pk':obj.id
    }
    if group is not None:
        filterKwargs['group']=group
    return Video.objects.filter(Q(hide=False) | Q(hide=None),**filterKwargs)

def build_url(url,q):
    params=[]
    for k in q:
        v=q[k]
        if v is None:
            v=''
        elif type(v).__name__!='unicode':
            v=str(v)
        v=urllib.quote(v.encode('utf-8'))
        k=urllib.quote(str(k).encode('utf-8'))
        params.append(k+'='+v)
    return url+'?'+"&".join(params)

def update_member_related_video(member,video):
    cnt=get_videos_queryset(member).filter(source_id=video['id'],source_type='youtube').count()
    if cnt==0:
        v = Video(
            embed_link=video['embed_url_autoplay'],
            small_image_link=video['thumbnail90x120'],
            title=video['title'],
            description=video['description'],
            link=video['link'],
            source_type='youtube', 
            source_id=video['id'],
            published=video['published'],
            group='related', 
            content_object=member
        )
        v.save()
        return v
    else:
        return False