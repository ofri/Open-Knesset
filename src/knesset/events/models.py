from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from knesset.persons.models import Person

class Event(models.Model):
    ''' hold the when, who, what, where and which fields of events
        and allows the users to contribute resources (through links)
        and discuss upcoming events.
    '''
    when = models.DateTimeField()
    who = models.ManyToManyField(Person)
    what = models.TextField()
    where = models.TextField()
    which_type   = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="event_for_%(class)s", null=True)
    which_pk = models.TextField(_('object ID'), null=True)
    which_object = generic.GenericForeignKey(ct_field="which_type", fk_field="which_pk")

    @property
    def is_future(self):
        return self.when > datetime.now()

    @property
    def which(self):
        return self.which_object and unicode(self.which_object) or self.what

    def get_absolute_url(self):
        if self.which_object:
            return '%s#event-%d' % (self.which_object.get_absolute_url(), self.id)
        else:
            return '#'
