# encoding: utf-8

from django.db import models

class LobbyistHistory(models.Model):
    """
    this model allows to see an overview over time of the lobbyists in the knesset
    if you just want the latest composition of lobbyists - get the last record (according to scrape_time)
    scrape_time might be null - that means the record is not fully scraped yet
    """
    scrape_time = models.DateTimeField(blank=True, null=True)
    lobbyists = models.ManyToManyField('lobbyists.Lobbyist', related_name='histories')

class Lobbyist(models.Model):
    """
    this model represents a single lobbyist and is connected to the LobbyistHistory.lobbyists field
    the lobbyist is connected to a single person
    and has a source_id which is the id we get from the knesset
    the actual lobbyist's details are stored in the LobbyistData model and related in the data field
    the LobbyistData model allows to see changes in lobbyist data over time
    to get just the latest data - get the latest record according to scrape_end_time
    """
    person = models.ForeignKey('persons.Person', blank=True, null=True, related_name='lobbyist')
    source_id = models.CharField(blank=True, null=True, max_length=20)

    def latest_data(self):
        return self.data.filter(scrape_time__isnull=False).latest('scrape_time')

class LobbyistData(models.Model):
    """
    this model represents the data of a lobbyist in a certain point of time
    it allows to see changes in a lobbyist details over time
    if you just want the latest data from a lobbyist - get the latest record according to scrape_time
    scrape_time might be null - that means the record is not fully scraped yet
    """
    lobbyist = models.ForeignKey('lobbyists.Lobbyist', blank=True, null=True, related_name='data')
    scrape_time = models.DateTimeField(blank=True, null=True)
    first_name = models.CharField(blank=True, null=True, max_length=100)
    family_name = models.CharField(blank=True, null=True, max_length=100)
    profession = models.CharField(blank=True, null=True, max_length=100)
    corporation_name = models.CharField(blank=True, null=True, max_length=100)
    corporation_id = models.CharField(blank=True, null=True, max_length=20)
    faction_member = models.CharField(blank=True, null=True, max_length=100)
    faction_name = models.CharField(blank=True, null=True, max_length=100)
    permit_type = models.CharField(blank=True, null=True, max_length=100)
    represents = models.ManyToManyField('lobbyists.LobbyistRepresent')

class LobbyistRepresent(models.Model):
    """
    this model represents a single represent record and is connected to the LobbyistData represents field
    each lobbyist data has a set of representations, this model is a single representation
    the source_id allows to recognize this representation and show it's changed over time
    the actual data is in the LobbyistRepresentData model and related here in the data field
    if you want just the current representation data, get the latest record according to scrape_end_time
    """
    source_id = models.CharField(blank=True, null=True, max_length=20)

class LobbyistRepresentData(models.Model):
    """
    the lobbyist represents data, related to LobbyistRepresent model
    allows to see changes of lobbyist representation details over time
    """
    lobbyist_represent = models.ForeignKey('lobbyists.LobbyistRepresent', blank=True, null=True, related_name='data')
    scrape_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=100)
    domain = models.CharField(blank=True, null=True, max_length=100)
    type = models.CharField(blank=True, null=True, max_length=100)
