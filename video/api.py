from datetime import date, timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from tastypie.constants import ALL

from apis.resources.base import BaseResource
from committees.models import Committee
from mks.models import Member
from models import Video


class VideoResource(BaseResource):

    class Meta(BaseResource.Meta):
        limit = 500
        queryset = Video.objects.all()
        allowed_methods = ['get']
        filtering = dict(
            object_pk=ALL,
            group=ALL,
        )

    def apply_filters(self, request, applicable_filters):
        qs = super(VideoResource, self).apply_filters(request,
                                                      applicable_filters)

        if 'object_type' in request.GET:
            object_type = request.GET['object_type']
            if object_type == 'member':
                modelObj = Member
            elif object_type == 'committee':
                modelObj = Committee
            else:
                modelObj = None

            if modelObj is not None:
                object_type = ContentType.objects.get_for_model(modelObj)
                qs = qs.filter(content_type__pk=object_type.id)
        if 'recent_published_days' in request.GET:
            recent_published_days = request.GET['recent_published_days']
            qs = qs.filter(
                Q(published__gt=date.today(
                ) - timedelta(days=int(recent_published_days)))
                | Q(sticky=True)
            )
        return qs

    def apply_sorting(self, obj_list, options=None):
        if 'order_by_published_sticky_first' in options:
            qs = obj_list.order_by('-sticky', '-published')
        else:
            qs = super(VideoResource, self).apply_sorting(obj_list, options)
        return qs
