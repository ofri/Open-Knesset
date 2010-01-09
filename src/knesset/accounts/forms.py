from django import forms
from django.contrib.auth.models import User, Permission
from socialauth.models import AuthMeta
from django.utils.translation import ugettext_lazy as _

class EditProfileForm(forms.Form):
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'size':'40'}),label=_(u'email address'))
    username = forms.CharField(max_length = 100, widget=forms.TextInput(attrs={'size':'40'}),label=_(u'user name'))
#    first_name = forms.CharField(max_length = 100, required=False, widget=forms.TextInput(attrs={'size':'40'}))
#    last_name = forms.CharField(max_length = 100, required=False, widget=forms.TextInput(attrs={'size':'40'}))
    
    def __init__(self, user=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.user:
            self.initial = {'username': user.username, \
                        'first_name':user.first_name, 'last_name':user.last_name}
        self.has_email = False        
        if self.user.authmeta.is_email_filled:
            self.initial['email'] = self.user.email
            self.has_email = True


        p = Permission.objects.get(name='Can add comment')
        self.has_perms = self.user.user_permissions.filter(id=p.id).count()
        
        
    def clean_username(self):      
        print "clean_username"
        data = self.cleaned_data['username']
        if data ==  self.user.username:
            return data
        try:
            User.objects.get(username = data)
            raise forms.ValidationError("This username is already taken.")
        except User.DoesNotExist:
            return data
    
    def clean(self):
        print "clean"
        cleaned_data = self.cleaned_data
        #if 'password' in cleaned_data and 'password2' in cleaned_data:
        #    if cleaned_data['password'] != cleaned_data['password2']:
        #        raise forms.ValidationError('The passwords do not match.')
        return cleaned_data      
        
    def save(self):
        user = self.user
        #print "self.cleaned_data = %s" % str (self.cleaned_data)
        if self.cleaned_data['email'] != None:
            if user.email != self.cleaned_data['email']: #email changed - user loses comment permissions, until he validates email again.
                p = Permission.objects.get(name='Can add comment')
                user.user_permissions.remove(p)

            user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        #user.first_name = self.cleaned_data['first_name']
        #user.last_name = self.cleaned_data['last_name']
        user.save()
        try:
            authmeta = user.authmeta
            authmeta.is_email_filled = True
            authmeta.is_profile_modified = True
            authmeta.save()
        except AuthMeta.DoesNotExist:
            pass
        return user
        
        
