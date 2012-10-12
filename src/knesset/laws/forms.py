from django import forms
from django.utils.translation import ugettext_lazy as _
from datetime import date
from tagging.models import Tag
from models import Vote
from vote_choices import ORDER_CHOICES, TAGGED_CHOICES, TYPE_CHOICES

class VoteSelectForm(forms.Form):
    """Votes filtering form"""

    vtype = forms.ChoiceField(label=_('Vote types'), choices=TYPE_CHOICES,
            required=False, initial='all')
    tagged = forms.ChoiceField(label=_('Tags'), choices=TAGGED_CHOICES,
            required=False, initial='all')
    order = forms.ChoiceField(label=_('Order by'), choices=ORDER_CHOICES,
            required=False, initial='time')
    from_date = forms.DateField(label=_('From date'), required=False)
    to_date = forms.DateField(label=_('To date'), required=False,
            initial=date.today)

    def __init__(self, *args, **kwargs):
        super(VoteSelectForm, self).__init__(*args, **kwargs)

        tags = Tag.objects.usage_for_model(Vote)
        new_choices = list(TAGGED_CHOICES)
        new_choices.extend([(t.name, t.name) for t in tags])
        self.fields['tagged'].choices = new_choices
