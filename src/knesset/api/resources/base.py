from tastypie.cache import SimpleCache
from tastypie.throttle import CacheThrottle
from tastypie.resources import ModelResource


class BaseResource(ModelResource):

    class Meta:
        cache = SimpleCache()
        throttle = CacheThrottle(throttle_at=60, timeframe=60)

    def alter_list_data_to_serialize(self, request, to_be_serialized):
        fields = getattr(self._meta, 'list_fields', None)
        if not fields:
            return to_be_serialized

        # copy the fields, we don't want to want to change the class attribute
        fields = fields[:]

        if self._meta.include_resource_uri:
            fields.append('resource_uri')

        extra_fields = request.GET.get('extra_fields')
        if extra_fields:
            fields.extend(x.strip() for x in extra_fields.split(',')
                          if x.strip())

        for bundle in to_be_serialized['objects']:
            # by default we only serve unicode and pk
            d = bundle.data

            bundle.data = dict((f, d.get(f)) for f in fields)

        return to_be_serialized
