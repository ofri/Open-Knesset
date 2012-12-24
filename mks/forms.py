from django import forms
from django.utils.translation import ugettext as _

class VerbsForm(forms.Form):
    verbs = forms.MultipleChoiceField(
                                choices=(('proposed', _('Proposed')),
                                         ('joined', _('Joined')),
                                         ('posted', _('Posted')),
                                         ('attended', _('Attended')),
                                         ('voted', _('Voted')),
                                        ),
                                label=_('Displaying Actions'),
                                required=False,
                                initial=['proposed','posted'],
                                widget=forms.CheckboxSelectMultiple)
