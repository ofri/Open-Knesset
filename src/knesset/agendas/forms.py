from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from models import Agenda, AgendaVote

class H4(forms.Widget):
    """ used to display header fields """
    input_type = None # Subclasses must define this.

    def render(self, name, value, attrs=None):
        return mark_safe(u'<h4>%s</h4>' % value)

class EditAgendaForm(forms.Form):
    name = forms.CharField(max_length=300, 
                           label=_(u'Agenda name'), 
                           error_messages={'required': _('Please enter an agenda name'),
                                           'max_length': _('Agenda name must be shorter than 300 characters')})                                                           
    public_owner_name = forms.CharField(max_length=100,
                                        label=_(u'Public owner name'),
                                        error_messages={'required': _('Please enter a public owner name'),
                                                        'max_length': _('Public owner name must be shorter than 100 characters')})
    description = forms.CharField(min_length=15, 
                                  label=_(u'Agenda description'), 
                                  error_messages={'required': _('Please enter a description for this agenda'),
                                                  'min_length': _('Agenda description must be at least 15 characters long')},
                                  widget=forms.Textarea)
    
    def __init__(self, agenda=None, *args, **kwargs):
        super(EditAgendaForm, self).__init__(*args, **kwargs)
        self.agenda = agenda
        if self.agenda is not None:
            self.initial = {'name': self.agenda.name,
                            'public_owner_name': self.agenda.public_owner_name,
                            'description': self.agenda.description,
                            }
   
class AddAgendaForm(ModelForm):
    # to have the same names and help texts as the edit form, we need to override the form fields definitions:
    name = forms.CharField(max_length=300, 
                           label=_(u'Agenda name'), 
                           error_messages={'required': _('Please enter an agenda name'),
                                           'max_length': _('Agenda name must be shorter than 300 characters')})
    public_owner_name = forms.CharField(max_length=100,
                                        label=_(u'Public owner name'),
                                        error_messages={'required': _('Please enter a public owner name'),
                                                        'max_length': _('Public owner name must be shorter than 100 characters')})
    description = forms.CharField(min_length=15, 
                                  label=_(u'Agenda description'), 
                                  error_messages={'required': _('Please enter a description for this agenda'),
                                                  'min_length': _('Agenda description must be at least 15 characters long')},
                                  widget=forms.Textarea)

    class Meta:
        model = Agenda
        fields = ('name', 'public_owner_name', 'description')

RELATION_CHOICES = (
    (-1.0,'-1'),
    (-0.5,'-.5'),
    (0.0, '0'),
    (0.5, '.5'),
    (1.0,'1'),
)
class VoteLinkingForm(forms.Form):
    # a form to help agendas' editors tie votes to agendas
    agenda_name = forms.CharField(widget=H4, required=False, label='')
    vote_id = forms.IntegerField(widget=forms.HiddenInput) #TODO: hide this!
    agenda_id = forms.IntegerField(widget=forms.HiddenInput) #TODO: hide this!
    weight = forms.TypedChoiceField(label=_('Weight'), choices=RELATION_CHOICES, 
            coerce=float, required=True, widget=forms.RadioSelect)
    reasoning = forms.CharField(required=False, max_length=300, 
                           label=_(u'Reasoning'), 
                           widget = forms.Textarea(attrs={'cols':30, 'rows':5}),
                           )
VoteLinkingFormSet = formset_factory(VoteLinkingForm, extra=0)

