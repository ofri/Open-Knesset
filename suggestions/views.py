import json

from django.db import models
from django.http import HttpResponse
from django.views.generic.base import View

from .models import Suggestion
from auxiliary.serializers import PromiseAwareJSONEncoder


class PendingSuggestionsCountView(View):
    """Return the pending suggestions for Model/Instance.

    The view can return the results for multiple models/objects. Pass each in
    the query string's ``for`` argument, e.g::

        ?for=auxiliary.Tidbit&for=events.Event&for=mks.Member-801

    The last one in the example above get's pending for Member instance with
    pk=801.
    """

    def get_models_and_instances(self, request):
        "Returns models/instances in GET param ``for``"

        items = request.GET.getlist('for')
        for item in items:
            try:
                model_name, pk = item.split('-', 1)
            except ValueError:
                model_name, pk = item, None

            model = models.get_model(*model_name.split('.', 1))

            if pk is None:
                yield model
            else:
                instance = model.objects.get(pk=pk)
                yield instance

    def get_pending(self, request):
        res = {}

        for model_or_instance in self.get_models_and_instances(request):
            if isinstance(model_or_instance, models.Model):
                key = unicode(model_or_instance)
            else:
                key = unicode(model_or_instance._meta.verbose_name)

            res[key] = Suggestion.objects.get_pending_suggestions_for(
                model_or_instance)

        return res

    def prepare_pending(self, result):
        "Prepares the QuerySet for the response"

        for key in result:
            result[key] = result[key].count()

        return result

    def get(self, request, *args, **kwargs):
        res = self.get_pending(request)
        res = self.prepare_pending(res)
        return HttpResponse(
            json.dumps(res, ensure_ascii=False, cls=PromiseAwareJSONEncoder),
            mimetype='application/json')


class PendingSuggestionsView(PendingSuggestionsCountView):

    def prepare_pending(self, result):
        "Prepares the QuerySet for the response"

        for key in result:
            result[key] = [unicode(x) for x in result[key]]

        return result
