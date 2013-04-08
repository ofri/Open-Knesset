import json
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.views.generic import ListView, TemplateView
from django.utils.translation import ugettext as _
from hashnav.detail import DetailView
from agendas.models import Agenda
from polyorg.models import CandidateList, Candidate


class CandidateListListView(ListView):
    model = CandidateList

    def get_queryset(self):
        cache_key = "candidate_list_list"
        qs = cache.get(cache_key, None)
        if not qs:
            qs = self.model.objects.filter(number_of_seats__gt=0).order_by('-number_of_seats')
            cache.set(cache_key, qs, settings.LONG_CACHE_TIME)
        return qs


class CandidateListDetailView(DetailView):

    model = CandidateList

    def get(self, request, **kwargs):
        # Don't allow Candidates without seats
        cl = self.get_object()

        if not cl.number_of_seats:
            raise Http404
        return super(CandidateListDetailView, self).get(request, **kwargs)

    def get_context_data (self, **kwargs):
        cache_key = "candidate_list_%(pk)s" % kwargs
        context = cache.get(cache_key)
        if not context:
            context = super(CandidateListDetailView, self).get_context_data(**kwargs)
            cl = context['object']
            context['head'] = cl.getHeadName()
            candidates = Candidate.objects.select_related('person',
                    'person__mk').filter(candidates_list=cl,
                                         ordinal__lte=cl.number_of_seats).order_by('ordinal')
            context['candidates'] = [x.person for x in candidates]
            agendas = []
            if cl.member_ids:
                for a in Agenda.objects.filter(is_public=True).order_by('-num_followers'):
                    agendas.append({'id': a.id,
                                    'name': a.name,
                                    'url': a.get_absolute_url(),
                                    'score': a.candidate_list_score(cl)})
                context['agendas'] = agendas
            cache.set(cache_key, context, settings.LONG_CACHE_TIME)
        return context

class CandidateListCompareView(TemplateView):
    """
    A comparison of candidate lists side-by-side
    """
    template_name = "polyorg/candidatelist_compare.html"

    def get_context_data(self, **kwargs):
        ctx = cache.get("candidate_list_compare")
        if not ctx:
            ctx = super(CandidateListCompareView, self).get_context_data(**kwargs)

            clists = [{'name': cl.name,
                       'ballot': cl.ballot,
                       'url': cl.get_absolute_url(),
                       'wikipedia_page': cl.wikipedia_page,
                       'facebook_url': cl.facebook_url,
                       'candidates': [{'id': person.id,
                                       'name': person.name,
                                       'img_url': person.img_url,
                                       'ordinal': None,  # TODO
                                       'gender': person.gender or 'X',
                                       'mk':getattr(person, "mk") is not None,
                                       'bills_stats_approved': person.mk.bills_stats_approved if person.mk else None,
                                       'bills_stats_proposed': person.mk.bills_stats_proposed if person.mk else None,
                                       'residence_centrality': person.residence_centrality,
                                       'role': person.roles.all()[0].text if person.roles.count() else None
                                      }
                                      for person in cl.candidates.order_by('candidate__ordinal')[:10]]}
                      for cl in CandidateList.objects.order_by('ballot')]

            ctx['candidate_lists'] = json.dumps(clists)
            cache.set("candidate_list_compare", ctx, settings.LONG_CACHE_TIME)
        return ctx
