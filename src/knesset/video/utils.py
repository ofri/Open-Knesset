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
