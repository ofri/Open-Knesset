from django.db import models
from django.utils.translation import ugettext_lazy as _

class AgendaVote(models.Model):
    agenda = models.ForeignKey('Agenda')
    vote = models.ForeignKey('laws.Vote')
    score = models.FloatField(default=0.0)
    reasoning = models.TextField(null=True,blank=True)
    

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