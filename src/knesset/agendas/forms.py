from django import forms
from django.forms import ModelForm
#from django.contrib.auth.models import User, Permission
#from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from models import Agenda

class EditAgendaForm(forms.Form):
    name = forms.CharField(max_length=300, label=_(u'Agenda name'), error_messages={'required': _('Please enter an agenda n'),
                                                                                     'max_length': _('Your agenda title be shorter than 300 characters')})
    description = forms.CharField(min_length=15, label=_(u'Agenda description'), error_messages={'required': _('Please enter a description for this agenda'),
                                                                                                 'min_length': _('Your agenda description must be at least 15 characters long')})
    
    def __init__(self, agenda=None, *args, **kwargs):
        super(EditAgendaForm, self).__init__(*args, **kwargs)
        self.agenda = agenda
        if self.agenda is not None:
            self.initial = {'name': self.agenda.name,
                            'description': self.agenda.description,
                            }
   
class AddAgendaForm(ModelForm):
    class Meta:
        model = Agenda
        fields = ('name', 'description')