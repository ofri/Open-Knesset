from django import forms

from models import Topic

class EditTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title','description','committees')
