from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.views.generic.list_detail import object_list, object_detail
from piston.emitters import Emitter

class DivEmitter(Emitter):
    """
    Emitter for the Django serialized format.
    """
    def render(self, request):
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, (int, str)):
            response = self.data
        elif isinstance(self.data, QuerySet):
            if self.data.count() > 1:
                response = object_list(request, queryset=self.data)
            else:
                response = object_detail(request, queryset=self.data,
                                       object_id=self.data[0].id)

        return response
        
