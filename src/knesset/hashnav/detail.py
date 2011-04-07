from django.views.generic.detail import DetailView
from django.http import HttpResponse

class DetailView(DetailView):

    def get(self, request, **kwargs):
        ''' overiding the default get just so to pass the aditional params '''
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)

    def head(self, request, *args, **kwargs):
        return HttpResponse()
