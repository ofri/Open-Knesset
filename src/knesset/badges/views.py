from django.views.generic.list_detail import object_list
from django.db.models import Count

from knesset.hashnav import DetailView, ListView
from knesset.badges.models import Badge, BadgeType


class BadgeTypeDetailView(DetailView):
    queryset = BadgeType.objects.all()
    template_name = 'badges/badge_detail.html'
    
    def get_context(self):
        context = super(BadgeTypeDetailView, self).get_context()
        context['badges'] = context['object'].badges.order_by('-created').all()
        return context

class BadgeTypeListView(ListView):
    queryset = BadgeType.objects.all().annotate(amount=Count('badges')).order_by('-amount')
    template_name = 'badges/all_badge_list.html'
    
