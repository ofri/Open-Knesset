# encoding: utf-8

from django.db import models
from django.core.cache import cache
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

class LobbyistHistoryManager(models.Manager):

    def latest(self):
        return self.filter(scrape_time__isnull=False).latest('scrape_time')


class LobbyistHistory(models.Model):
    """
    this model allows to see an overview over time of the lobbyists in the knesset
    to get the latest lobbyist history object, use LobbyistHistory.objects.latest
    """
    scrape_time = models.DateTimeField(blank=True, null=True)
    lobbyists = models.ManyToManyField('lobbyists.Lobbyist', related_name='histories')

    objects = LobbyistHistoryManager()

    @property
    def corporations(self):
        """
        Returns all the corporations associated with this point in time of the lobbyist history
        Because it executes a lot of queries - it is cached for 1 day
        TODO: optimize it
        """
        corporation_ids = cache.get('LobbyistHistory_%d_corporation_ids' % self.id)
        if not corporation_ids:
            corporation_ids = []
            for lobbyist in self.lobbyists.all():
                corporation_id = lobbyist.cached_data['latest_corporation']['id']
                if corporation_id not in corporation_ids:
                    corporation_ids.append(corporation_id)
            cache.set('LobbyistHistory_%d_corporation_ids' % self.id, corporation_ids, 86400)
        return LobbyistCorporation.objects.filter(id__in=corporation_ids)

    @property
    def main_corporations(self):
        """
        Returns all the main corporations (e.g. without alias corporations and without 1 lobbyist corporations)
        """
        alias_corporation_ids = [ca.alias_corporation.id for ca in LobbyistCorporationAlias.objects.all()]
        return self.corporations.exclude(id__in = alias_corporation_ids)

    def clear_corporations_cache(self):
        cache.delete('LobbyistHistory_%d_corporation_ids' % self.id)


class Lobbyist(models.Model):
    """
    this model represents a single lobbyist and is connected to the LobbyistHistory.lobbyists field
    the lobbyist is connected to a single person
    and has a source_id which is the id we get from the knesset
    the actual lobbyist's details are stored in the LobbyistData model and related in the data field
    the LobbyistData model allows to see changes in lobbyist data over time
    to get just the latest data use - lobbyist.latest_data
    """
    person = models.ForeignKey('persons.Person', blank=True, null=True, related_name='lobbyist')
    source_id = models.CharField(blank=True, null=True, max_length=20)

    @cached_property
    def latest_data(self):
        return self.data.filter(scrape_time__isnull=False).latest('scrape_time')

    @cached_property
    def latest_corporation(self):
        return self.lobbyistcorporationdata_set.filter(scrape_time__isnull=False).latest('scrape_time').corporation

    @cached_property
    def cached_data(self):
        data = cache.get('Lobbyist_cached_data_%s' % self.id)
        if not data:
            data = {
                'id': self.id,
                'display_name': unicode(self.person),
                'latest_data': {
                    'profession': self.latest_data.profession,
                    'faction_member': self.latest_data.faction_member,
                    'faction_name': self.latest_data.faction_name,
                    'permit_type': self.latest_data.permit_type,
                    'scrape_time': self.latest_data.scrape_time,
                },
                'latest_corporation': {
                    'name': self.latest_corporation.name,
                    'id': self.latest_corporation.id,
                },
            }
            cache.set('Lobbyist_cached_data_%s' % self.id, data, 86400)
        return data

    def __unicode__(self):
        return self.person


class LobbyistDataManager(models.Manager):

    def latest_lobbyist_corporation(self, corporation_id):
        return self.filter(corporation_id = corporation_id, scrape_time__isnull=False).latest('scrape_time')

    def get_corporation_lobbyists(self, corporation_id):
        lobbyists = []
        for lobbyist in LobbyistHistory.objects.latest().lobbyists.all():
            lobbyists.append(lobbyist) if lobbyist.latest_data.corporation_id == corporation_id else None
        return lobbyists


class LobbyistData(models.Model):
    """
    this model represents the data of a lobbyist in a certain point of time
    it allows to see changes in a lobbyist details over time
    if you just want the latest data from a lobbyist - get the latest record according to scrape_time
    scrape_time might be null - that means the record is not fully scraped yet
    """
    lobbyist = models.ForeignKey('lobbyists.Lobbyist', blank=True, null=True, related_name='data')
    scrape_time = models.DateTimeField(blank=True, null=True)
    source_id = models.CharField(blank=True, null=True, max_length=20)
    first_name = models.CharField(blank=True, null=True, max_length=100)
    family_name = models.CharField(blank=True, null=True, max_length=100)
    profession = models.CharField(blank=True, null=True, max_length=100)
    corporation_name = models.CharField(blank=True, null=True, max_length=100)
    corporation_id = models.CharField(blank=True, null=True, max_length=20)
    faction_member = models.CharField(blank=True, null=True, max_length=100)
    faction_name = models.CharField(blank=True, null=True, max_length=100)
    permit_type = models.CharField(blank=True, null=True, max_length=100)
    represents = models.ManyToManyField('lobbyists.LobbyistRepresent')

    objects = LobbyistDataManager()


    def __unicode__(self):
        return '%s %s'%(self.first_name, self.family_name)


class LobbyistCorporationManager(models.Manager):

    def current_corporations(self):
        return LobbyistHistory.objects.latest().corporations


class LobbyistCorporation(models.Model):
    """
    This represents a lobbyist corporation
    the source_id is the corporation's het-pey
    each lobbyist corporation has a group of lobbyists - this can change over time so represented in the LobbyistCorporationData model
    to get the latest data use lobbyist_corporation.latest_data
    """
    name = models.CharField(blank=True, null=True, max_length=100)
    source_id = models.CharField(blank=True, null=True, max_length=20)

    objects = LobbyistCorporationManager()

    @cached_property
    def latest_data(self):
        return self.data.filter(scrape_time__isnull=False).latest('scrape_time')

    @property
    def lobbyists_count(self):
        return self.latest_data.lobbyists.count()

    @property
    def combined_lobbyists_count(self):
        lobbyists_count = self.lobbyists_count
        for ca in LobbyistCorporationAlias.objects.filter(main_corporation__id=self.id):
            lobbyists_count = lobbyists_count + ca.alias_corporation.combined_lobbyists_count
        return lobbyists_count

    @cached_property
    def cached_data(self):
        data = cache.get('LobbyistCorporation_cached_data_%s' % self.id)
        if not data:
            data = {
                'id': self.id,
                'name': self.name,
                'source_id': self.latest_data.source_id,
                'combined_lobbyists_count': self.combined_lobbyists_count
            }
            cache.set('LobbyistCorporation_cached_data_%s' % self.id, data, 86400)
        return data

    def clear_cache(self):
        cache.delete('LobbyistCorporation_cached_data_%s' % self.id)

    def __unicode__(self):
        return self.name


class LobbyistCorporationAliasManager(models.Manager):

    def create(self, *args, **kwargs):
        if len(args) > 1:
            for id in args[1:]:
                kwargs = {'main_corporation_id': args[0], 'alias_corporation_id': id}
                super(LobbyistCorporationAliasManager, self).create(**kwargs)
        else:
            return super(LobbyistCorporationAliasManager, self).create(**kwargs)


class LobbyistCorporationAlias(models.Model):
    """
    In the source data there are sometimes different coroprations
    which are actually the same one.
    For example - there are sometimes typos in the corporation id which cause
    our scraper to think it's different corporations
    This model allows to link this corporations so we can treat them as the same corporation
    """
    main_corporation = models.ForeignKey('lobbyists.LobbyistCorporation', related_name='lobbyistcorporationalias_main')
    alias_corporation = models.ForeignKey('lobbyists.LobbyistCorporation', related_name='lobbyistcorporationalias_alias', unique=True)

    objects = LobbyistCorporationAliasManager()


class LobbyistCorporationData(models.Model):
    """
    This represents data about a corporation which might change over time
    currently the only relevant data is the lobbyists which are members of the corporation
    """
    corporation = models.ForeignKey('lobbyists.LobbyistCorporation', blank=True, null=True, related_name='data')
    scrape_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=100)
    source_id = models.CharField(blank=True, null=True, max_length=20)
    lobbyists = models.ManyToManyField('lobbyists.Lobbyist')

    def __unicode__(self):
        return self.name

    
class LobbyistRepresent(models.Model):
    """
    this model represents a single represent record and is connected to the LobbyistData represents field
    each lobbyist data has a set of representations, this model is a single representation
    the source_id allows to recognize this representation and show it's changed over time
    the actual data is in the LobbyistRepresentData model and related here in the data field
    if you want just the current representation data, get the latest record according to scrape_end_time
    """
    source_id = models.CharField(blank=True, null=True, max_length=20)
    name = models.CharField(blank=True, null=True, max_length=100)

    @property
    def latest_data(self):
        return self.data.filter(scrape_time__isnull=False).latest('scrape_time')

    def __unicode__(self):
        return self.latest_data.name

        
class LobbyistRepresentData(models.Model):
    """
    the lobbyist represents data, related to LobbyistRepresent model
    allows to see changes of lobbyist representation details over time
    """
    lobbyist_represent = models.ForeignKey('lobbyists.LobbyistRepresent', blank=True, null=True, related_name='data')
    scrape_time = models.DateTimeField(blank=True, null=True)
    source_id = models.CharField(blank=True, null=True, max_length=20)
    name = models.CharField(blank=True, null=True, max_length=100)
    domain = models.CharField(blank=True, null=True, max_length=100)
    type = models.CharField(blank=True, null=True, max_length=100)
