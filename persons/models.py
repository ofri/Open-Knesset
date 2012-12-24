from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms.fields import IntegerField

class Title(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

class PersonAlias(models.Model):
    name = models.CharField(max_length=64)
    person = models.ForeignKey('Person')
    
    def __unicode__(self):
        return "%s -> %s" % (self.name, self.person.name)

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

    def merge(self, other):
        """make other into an alias of self"""
        if other.mk:
            if self.mk and self.mk != other.mk:
                # something is wrong, we are trying to merge two persons with non matching MKs
                raise ValidationError('Trying to merge persons with non matching MKs')
            self.mk = other.mk
        for title in other.titles.all():
            self.titles.add(title)
        for role in other.roles.all():
            role.person = self
            role.save()
        (pa,created) = PersonAlias.objects.get_or_create(name=other.name,person=self)
        if created:
            pa.save()
        for part in other.protocol_parts.all():
            part.speaker = self
            part.save()
        other.delete()
        self.save()
        
class Role(models.Model):
    text = models.CharField(blank=True,null=True, max_length=1024)
    person = models.ForeignKey(Person, related_name='roles')

    def __unicode__(self):
        return self.text
 
class ProcessedProtocolPart(models.Model):
    """This model is used to keep track of protocol parts already searched for creating persons.
       There should be only 1 record in it, with the max id of a protocol part searched"""
    protocol_part_id = models.IntegerField()     
