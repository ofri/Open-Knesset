'''
Api for planet and tags
'''

from tastypie.exceptions import InvalidFilterError
from tastypie.constants import ALL
import tastypie.fields as fields
from apis.resources.base import BaseResource
from planet.models import Feed, Post
from mks.models import Member
from links.models import Link
from tagging.models import Tag, TaggedItem
from django.contrib.contenttypes.models import ContentType
from django.conf.urls.defaults import url
from django.http import Http404
from django.shortcuts import get_object_or_404

from laws.models import Vote, Bill
from committees.models import CommitteeMeeting

from operator import attrgetter


class PostResource(BaseResource):

    class Meta:
        limit = 50
        allowed_methods = ['get']
        fields = ['id', 'title', 'date_created', 'url', 'content']

        queryset = Post.objects.all()
        resource_name = "posts"
        filtering = {
            'member_id': ALL,
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(PostResource, self).build_filters(filters)

        if "member_id" in filters:
            try:
                member = Member.objects.get(pk=filters['member_id'])
            except Member.DoesNotExist:
                raise InvalidFilterError("Could not find member id %s" % filters['member_id'])
            links = Link.objects.for_model(member)
            feeds = Feed.objects.filter(url__in=map(lambda x: x.url, links), is_active=True)

            orm_filters["feed__in"] = feeds

        return orm_filters


class TagResource(BaseResource):
    ''' Tagging API
    '''

    number_of_items = fields.IntegerField()

    class Meta:
        queryset = Tag.objects.all().order_by('name')
        allowed_methods = ['get']
        include_absolute_url = True
        list_fields = ['id', 'name']

    TAGGED_MODELS = (Vote, Bill, CommitteeMeeting)

    def obj_get_list(self, filters=None, **kwargs):
        all_tags = list(set().union(*[Tag.objects.usage_for_model(model) for model in self.TAGGED_MODELS]))
        all_tags.sort(key=attrgetter('name'))
        return all_tags

    def dehydrate_number_of_items(self, bundle):
        return bundle.obj.items.count()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/$' % self._meta.resource_name, self.wrap_view('get_object_tags'), name='tags-for-object'),
            url(r'^(?P<resource_name>%s)/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/(?P<related_name>[_a-zA-Z]\w*)/$' % self._meta.resource_name, self.wrap_view('get_related_tags'), name='related-tags'),
        ]

    def _create_response(self, request, objects):
        bundles = []
        for result in objects:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            bundles.append(bundle)

        return self.create_response(request, {'objects': bundles})

    def get_related_tags(self, request, **kwargs):
        """ Can be used to get all tags used by all CommitteeMeetings of a specific committee
        """
        try:
            ctype = ContentType.objects.get_by_natural_key(kwargs['app_label'], kwargs['object_type'])
        except ContentType.DoesNotExist:
            raise Http404('Object type not found.')

        model = ctype.model_class()
        container = get_object_or_404(model, pk=kwargs['object_id'])
        try:
            related_objects = getattr(container, kwargs['related_name']).all()
        except AttributeError:
            raise Http404('Related name not found.')

        tags = Tag.objects.usage_for_queryset(related_objects)

        return self._create_response(request, tags)

    def get_object_tags(self, request, **kwargs):
        ctype = None
        try:
            ctype = ContentType.objects.get_by_natural_key(kwargs['app_label'], kwargs['object_type'])
        except ContentType.DoesNotExist:
            pass

        tags_ids = TaggedItem.objects.filter(object_id=kwargs['object_id']).filter(content_type=ctype).values_list('tag', flat=True)
        tags = Tag.objects.filter(id__in=tags_ids)
        return self._create_response(request, tags)
