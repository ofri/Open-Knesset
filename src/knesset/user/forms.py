from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^(?u)\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only"),
        error_message = _("This value must contain only letters, numbers and underscores."))
    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

                     
