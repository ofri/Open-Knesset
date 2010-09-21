from django.db import models
from django.utils.translation import ugettext_lazy as _

class Title(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=64)
    mk = models.ForeignKey('mks.Member', blank=True, null=True, related_name='person')
    titles = models.ManyToManyField(Title, blank=True, null=True, related_name='persons')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        
    @models.permalink
    def get_absolute_url(self):
        return ('person-detail', [str(self.id)])
    
    def number_of_meetings(self):
        return self.protocol_parts.values('meeting').distinct().count()

    def number_of_committees(self):
        return self.protocol_parts.values('meeting__committee').distinct().count()

        
class Role(models.Model):
    text = models.CharField(blank=True,null=True, max_length=1024)
    person = models.ForeignKey(Person, related_name='roles')

    def __unicode__(self):
        return self.text
    
