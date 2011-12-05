from django.contrib.contenttypes.models import ContentType
from knesset.video.models import Video

def get_videos_queryset(object,group=None):
    object_type=ContentType.objects.get_for_model(object)
    filterKwargs={
        'content_type__pk':object_type.id,
        'object_pk':object.id
    }
    if group is not None:
        filterKwargs['group']=group
    return Video.objects.filter(**filterKwargs)
    
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

