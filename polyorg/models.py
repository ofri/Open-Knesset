from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class CandidatesList(models.Model):
    candidates = models.ManyToManyField('persons.Person', blank=True, null=True, through='Candidate')
    name = models.CharField(_('Name'), max_length = 80)
    ballot = models.CharField(_('Ballot'), max_length=4)
    number_of_seats = models.IntegerField(blank=True, null=True)
    surplus_partner = models.ForeignKey('self', blank=True, null=True, help_text=_('The list with which is the surplus votes partner'))

    def save(self, *args, **kwargs):
        super(CandidatesList, self).save()
        if self.surplus_partner:
            self.surplus_partner.surplus_partner = self


class Party(models.Model):
    name        = models.CharField(max_length=64)
    number_of_seats = models.IntegerField(blank=True, null=True)

class Candidate(models.Model):
    candidates_list = models.ForeignKey(CandidatesList)
    person = models.ForeignKey('persons.Person')
    ordinal = models.IntegerField(_('Ordinal'))
    party = models.ForeignKey(Party, blank=True, null=True)
    votes = models.IntegerField(_('Number of Votes in the last elections'), null=True, blank=True)
