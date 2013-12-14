from tagging.models import Tag, TaggedItem
from django.contrib.contenttypes.models import ContentType


def approve(admin, request, tag_suggestions):
    for tag_suggestion in tag_suggestions:
        obj = tag_suggestion.object

        ct = ContentType.objects.get_for_model(obj)

        tag, t_created = Tag.objects.get_or_create(name=tag_suggestion.name)
        ti, ti_created = TaggedItem.objects.get_or_create(
            tag=tag, object_id=obj.pk, content_type=ct)

        tag_suggestion.delete()
