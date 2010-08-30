from django.db import models
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
        return score_to_score_text[self.score]
    

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