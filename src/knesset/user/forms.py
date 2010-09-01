from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from knesset.mks.models import GENDER_CHOICES


class RegistrationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^(?u)[ \w.@+-]{4,}$',
        help_text = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."),
        error_message = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."))
    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EditProfileForm(forms.Form):
    email = forms.EmailField(required=False ,label=_(u'email address'),
                             help_text = _("We don't spam, and don't show your email to anyone")
                             )
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^(?u)[ \w.@+-]{4,}$',
        help_text = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."),
        error_message = _("Required. 4-30 characters (only letters, numbers spaces and @/./+/-/_ characters)."))

    public_profile = forms.BooleanField(label=_('Public profile'),
                                        help_text = _('Allow other users to view your profile on the site'))
    gender = forms.ChoiceField(choices = GENDER_CHOICES, 
                               label=_('Gender'))
    description = forms.CharField(label=_('Tell us and other users bit about yourself'), 
                                  widget=forms.Textarea)   

    def __init__(self, user=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.userprofile = user.get_profile()
        if self.user:
            self.initial = {'username': user.username,
                        'first_name':user.first_name,
                        'last_name':user.last_name,
                        'email': user.email,
                        'public_profile': self.userprofile.public_profile,
                        'gender': self.userprofile.gender,
                        'description': self.userprofile.description,
                        }
        self.has_email = True if user.email else False

        p = Permission.objects.get(name='Can add comment')
        self.has_perms = self.user.user_permissions.filter(id=p.id).count()

    def clean_username(self):
        data = self.cleaned_data['username']
        if data ==  self.user.username:
            return data
        try:
            User.objects.get(username = data)
            raise forms.ValidationError("This username is already taken.")
        except User.DoesNotExist:
            return data

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data

    def save(self, commit = True):
        user = self.user
        if self.cleaned_data['email'] != None:
            if user.email != self.cleaned_data['email']: #email changed - user loses comment permissions, until he validates email again.
                p = Permission.objects.get(name='Can add comment')
                user.user_permissions.remove(p)

            user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        self.userprofile.gender = self.cleaned_data['gender']
        self.userprofile.public_profile = self.cleaned_data['public_profile']
        self.userprofile.description = self.cleaned_data['description']
        
        if commit:
            user.save()
            self.userprofile.save()
        return user
