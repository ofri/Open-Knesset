from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
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
    name = models.CharField(max_length=300,unique=True)
    description = models.TextField(null=True,blank=True)
    editors = models.ManyToManyField('auth.User')
    votes = models.ManyToManyField('laws.Vote',through=AgendaVote)

    class Meta:
        verbose_name = _('Agenda')
        verbose_name_plural = _('Agendas')

    def __unicode__(self):
        return "%s" % self.name

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
