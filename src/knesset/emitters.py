from django.http import HttpResponse
from django.views.generic.list_detail import object_list
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
        else:
            response = object_list(request, queryset=self.data)

        return response
        
