from django import forms
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _

class EditProfileForm(forms.Form):
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'size':'40'}),label=_(u'email address'))
    username = forms.CharField(max_length = 100, widget=forms.TextInput(attrs={'size':'40'}),label=_(u'user name'))
    
    def __init__(self, user=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.user:
            self.initial = {'username': user.username, \
                        'first_name':user.first_name, 'last_name':user.last_name}

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
        if commit:
            user.save()
        return user
        
        
