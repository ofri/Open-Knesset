from operator import itemgetter

from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from actstream.models import Follow 

from knesset.mks.models import Party, Member

score_text_to_score = {'complies-fully':         1.0,
                       'complies-partially':     0.5,
                       'agnostic':               0.0,
                       'opposes-partially':     -0.5,
                       'opposes-fully':         -1.0,
                       }

score_to_score_text = dict(zip(score_text_to_score.values(), score_text_to_score.keys()))

class AgendaVote(models.Model):
    agenda = models.ForeignKey('Agenda')
    vote = models.ForeignKey('laws.Vote')
    score = models.FloatField(default=0.0)
    reasoning = models.TextField(null=True,blank=True)
    
    def set_score_by_text(self,score_text):
        self.score = score_text_to_score[score_text]
    def get_text_score(self):
        try:
            return score_to_score_text[self.score]
        except KeyError:
            return None
    

class Agenda(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    editors = models.ManyToManyField('auth.User')
    votes = models.ManyToManyField('laws.Vote',through=AgendaVote)
    public_owner_name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = _('Agenda')
        verbose_name_plural = _('Agendas')
        unique_together = (("name", "public_owner_name"),)

    def __unicode__(self):
        return "%s %s %s" % (self.name,_('by'),self.public_owner_name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('agenda-detail', [str(self.id)])

    @models.permalink
    def get_edit_absolute_url(self):
        return ('agenda-detail-edit', [str(self.id)])
    
    def mk_score(self, member):
        # Find all votes that
        #   1) This agenda is ascribed to
        #   2) the member participated in and either voted for or against
        for_score       = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="for").distinct().aggregate(Sum('score'))['score__sum']
        against_score   = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="against").distinct().aggregate(Sum('score'))['score__sum']
        if for_score == None:
            for_score = 0 
        if against_score == None:
            against_score = 0 
        return (for_score - against_score)
    
    def party_score(self, party):
        # party_members_ids = party.members.all().values_list('id',flat=True)
        for_score       = AgendaVote.objects.filter(agenda=self,vote__voteaction__member__in=party.members.all(),vote__voteaction__type="for").aggregate(Sum('score'))['score__sum']
        against_score   = AgendaVote.objects.filter(agenda=self,vote__voteaction__member__in=party.members.all(),vote__voteaction__type="against").aggregate(Sum('score'))['score__sum']
        if for_score == None:
            for_score = 0 
        if against_score == None:
            against_score = 0 
        return (for_score - against_score)

    def number_of_followers(self):
        return Follow.objects.filter(content_type=ContentType.objects.get(app_label="agendas", model="agenda").id,object_id=self.id).count() 
    
    def selected_mks(self, top=3, bottom=3):
        mks_and_significance = []
        for mk in Member.objects.all():
            score = self.mk_score(mk)
            if score >= 0:
                for_against = 'for'
            else:
                for_against = 'against'
            significance = score * self.number_of_followers()
            mks_and_significance.append({'mk':mk,
                                         'score':score,
                                         'class':for_against,
                                         'significance':significance})
        mks_and_significance.sort(key=itemgetter('significance'))
        if len(mks_and_significance) < top+bottom:
            delta = top+bottom - len(mks_and_significance)
            bottom = bottom - delta/2
            if delta%2:
                top = top - delta/2 +1
            else:
                top = top - delta/2
        
        if top and bottom:
            top_mks = mks_and_significance[-top:]
            bottom_mks = mks_and_significance[:bottom]
        elif top:
            top_mks = mks_and_significance[-top:]
            bottom_mks = []
        else:
            top_mks = []
            bottom_mks = []

        top_mks.sort(key=itemgetter('score'), reverse=True)        
        bottom_mks.sort(key=itemgetter('score'), reverse=True)
                
        return {'top': top_mks,
                'bottom': bottom_mks}
             

    def selected_parties(self, top=3, bottom=3):
        parties_and_significance = []
        for party in Party.objects.all():
            score = self.party_score(party)
            if score >= 0:
                for_against = 'for'
            else:
                for_against = 'against'
            significance = score * self.number_of_followers()
            parties_and_significance.append({'party':party,
                                             'score':score,
                                             'class':for_against,
                                             'significance':significance})
        parties_and_significance.sort(key=itemgetter('significance'))
        
        if top and bottom:
            top_parties = parties_and_significance[-top:]
            bottom_parties = parties_and_significance[:bottom]
        elif top:
            top_parties = parties_and_significance[-top:]
            bottom_parties = []
        else:
            top_parties = []
            bottom_parties = []

        top_parties.sort(key=itemgetter('score'), reverse=True)        
        bottom_parties.sort(key=itemgetter('score'), reverse=True)
                
        return {'top': top_parties,
                'bottom': bottom_parties}
             

from listeners import *
