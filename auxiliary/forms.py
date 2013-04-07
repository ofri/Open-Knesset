from django import forms
from django.utils.translation import ugettext_lazy as _

from suggestions.models import Suggestion, CREATE
from .models import ICON_CHOICES, Tidbit


class SearchForm(forms.Form):
    q = forms.CharField()


class TidbitSuggestionForm(forms.Form):
    title = forms.CharField(label=_('Title'), max_length=40,
                            initial=_('Did you know ?'))
    icon = forms.ChoiceField(label=_('Icon'), choices=ICON_CHOICES)
    content = forms.CharField(label=_('Content'), widget=forms.Textarea)
    button_text = forms.CharField(label=_('Button text'), max_length=100)
    button_link = forms.CharField(label=_('Button link'), max_length=255)

    def save(self, suggested_by):
        "Create the Suggestion object"

        data = {'suggested_by': suggested_by}
        for k in self.fields.keys():
            data[k] = self.cleaned_data[k]

        Suggestion.objects.create_suggestion(
            suggested_by=suggested_by,
            actions=[
                {
                    'action': CREATE,
                    'fields': data,
                    'subject': Tidbit,
                },
            ]
        )
