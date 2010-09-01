from django.http import HttpResponseRedirect
from base import View
from list import ListView
from detail import DetailView

class FormView(View):
    def POST(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        form = self.get_form(obj, *args, **kwargs)
        if form.is_valid():
            self.process_form(obj, form.cleaned_data)
            return HttpResponseRedirect(self.redirect_to(obj))
        template = self.get_template(obj)
        context = self.get_context(obj)
        mimetype = self.get_mimetype(obj)
        response = self.get_response(obj, template, context, mimetype=mimetype)
        return response

    def get_form(self, obj, *args, **kwargs):
        raise NotImplementedError

    def process_form(self, obj, data):
        raise NotImplementedError

    def redirect_to(self, obj):
        raise NotImplementedError


class CreateView(ListView, FormView):
    pass


class UpdateView(DetailView, FormView):
    # FIXME: Er, perhaps not PUT
    def put(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        # Force evaluation to populate PUT
        self.request.POST
        self.request.PUT = self.request._post
        del self.request._post
        return self.post(*args, **kwargs)


class DeleteView(DetailView):
    def delete(self, *args, **kwargs):
        obj = self.get_object( *args, **kwargs)
        obj.delete()
        return HttpResponseRedirect(self.redirect_to(obj))

    def post(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def redirect_to(self, obj):
        raise NotImplementedError

