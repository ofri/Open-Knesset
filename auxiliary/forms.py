from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput({'class': 'query'}))
    
