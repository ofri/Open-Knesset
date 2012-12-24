from django.views.generic.list_detail import object_list
from django.db.models import Count

from hashnav import DetailView, ListView
from models import Badge, BadgeType

class BadgeTypeDetailView(DetailView):
    model = BadgeType
    template_name = 'badges/badge_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BadgeTypeDetailView, self).get_context_data(*args, **kwargs)
        context['badges'] = context['object'].badges.order_by('-created').all()
        return context

class BadgeTypeListView(ListView):
    queryset = BadgeType.objects.all().annotate(amount=Count('badges')).order_by('-amount')
    template_name = 'badges/all_badge_list.html'
