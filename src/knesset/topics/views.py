from django.views.generic import ListView
from models import Topic

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'

