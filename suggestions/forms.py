from django import forms
from crispy_forms.helper import FormHelper

from suggestions.models import Suggestion, CREATE


class BaseSuggestionForm(forms.Form):
    "Base form for Suggestion forms"

    class Meta:
        model = None  # Change this for children. This model is used to
                      # generate the ajax request for displaying pending
                      # suggestions

        caption = None  # Used to generate the modal's caption

    def __init__(self, *args, **kwargs):
        suggested_pk = kwargs.pop('for_pk', None)
        super(BaseSuggestionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = 'main'
        self.helper.html5_required = True

        meta = self.Meta.model._meta
        model_name = '{0.app_label}.{0.object_name}'.format(meta)

        self.helper.attrs = {'data-for-model': model_name}

        if suggested_pk:
            self.helper.attrs['data-for-pk'] = suggested_pk

    @property
    def modal_caption(self):
        return self.Meta.caption

    def get_data(self):
        """Get the data for the action creation """
        data = {}
        for k in self.fields.keys():
            data[k] = self.cleaned_data[k]
        return data

    def save(self, suggested_by):
        "Implementations should override this"
        raise NotImplementedError


class InstanceCreateSuggestionForm(BaseSuggestionForm):

    def save(self, suggested_by):
        Suggestion.objects.create_suggestion(
            suggested_by=suggested_by,
            actions=[
                {
                    'action': CREATE,
                    'fields': self.get_data(),
                    'subject': self.Meta.model,
                },
            ]
        )
