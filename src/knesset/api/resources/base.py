from tastypie.cache import SimpleCache
from tastypie.resources import ModelResource

class BaseResource(ModelResource):
    class Meta:
        cache = SimpleCache()

    def dispatch(self, request_type, request, **kwargs):
        #this allows to hide fields for list view
        if request_type=='list':
            for fieldName in getattr(self._meta,'exclude_from_list_view',[]):
                if fieldName in self.fields: del self.fields[fieldName]
        return super(BaseResource,self).dispatch(request_type, request, **kwargs)
