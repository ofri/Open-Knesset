from django import forms
from django.forms import ModelForm
#from django.contrib.auth.models import User, Permission
#from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from models import Agenda, AgendaVote

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
    (-1,'-1'),
    (0, '0'),
    (1,'1'),
)
class VoteLinkingForm(forms.Form):
    # a form to help agendas' editors tie votes to agendas
    rel = forms.ChoiceField(choices=RELATION_CHOICES, required=True, widget=forms.RadioSelect)
    reasoning = forms.CharField(required=False, max_length=300, 
                           label=_(u'Reasoning'), 
                           widget = forms.Textarea,
                           )
