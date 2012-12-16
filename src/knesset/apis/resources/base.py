from django.conf import settings
from tastypie.cache import SimpleCache
from tastypie.resources import ModelResource
from tastypie.throttle import CacheThrottle

# are we using DummyCache ?
_cache = getattr(settings, 'CACHES', {})
_cache_default = _cache.get('default')
_is_dummy = _cache_default and _cache_default['BACKEND'].endswith('DummyCache')


class SmartCacheThrottle(CacheThrottle):
    "Make sure throttling works with DummyCache"

    def should_be_throttled(self, identifier, **kwargs):
        # Tastypie breaks when using dummy cache.  if cache type is dummy
        # we'll pretend the key wasn't found
        if _is_dummy:
            return False

        return super(SmartCacheThrottle, self).should_be_throttled(
            identifier, **kwargs)


class BaseResource(ModelResource):

    """Adds to Meta the following options:

    * ``list_fields``: The fields to display in resources listing

    For list mode, on may add to ``extra_fields`` to GET params to get
    addtional comma separated field in case one need more fields than those
    specified in ``list_fields``. e.g:

        GET /api/v2/some_resource/?extra_fields=img_url,number_of_children
    """

    class Meta:
        cache = SimpleCache()
        throttle = SmartCacheThrottle(throttle_at=60, timeframe=60)

    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.
        We overide here, to add optional ``fields`` in calls to full_dehydrate
        in case the resource specifies ``list_fields`` (and optional
        ``extra_fields`` in GET).

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        # impossible.
        objects = self.obj_get_list(request=request, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_list_uri(), limit=self._meta.limit)
        to_be_serialized = paginator.page()

        field_names = getattr(self._meta, 'list_fields', None)
        if field_names:
            field_names = field_names[:]
            extra_fields = request.GET.get('extra_fields', None)

            if extra_fields:
                field_names.extend(x.strip() for x in extra_fields.split(',')
                                   if x.strip())
            if getattr(self._meta, 'include_resource_uri', False):
                field_names.append('resource_uri')
            if getattr(self._meta, 'include_absolute_url', False):
                field_names.append('absolute_url')

            fields = dict((name, obj) for name, obj in self.fields.iteritems()
                          if name in field_names)
        else:
            fields = None

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [self.full_dehydrate(bundle, fields) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def full_dehydrate(self, bundle, fields=None):
        """
        Given a bundle with an object instance, extract the information from it
        to populate the resource.

        We override this to take into account optional fields in case of
        ``list``.
        """
        # Dehydrate each field.
        if fields is None:
            fields = self.fields

        for field_name, field_object in fields.items():
            # A touch leaky but it makes URI resolution work.
            if getattr(field_object, 'dehydrated_type', None) == 'related':
                field_object.api_name = self._meta.api_name
                field_object.resource_name = self._meta.resource_name

            bundle.data[field_name] = field_object.dehydrate(bundle)

            # Check for an optional method to do further dehydration.
            method = getattr(self, "dehydrate_%s" % field_name, None)

            if method:
                bundle.data[field_name] = method(bundle)

        bundle = self.dehydrate(bundle)
        return bundle
