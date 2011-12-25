from datetime import datetime, timedelta

# TODO x2: python-vobject in fedora <- are we tracking distribution locations somewhere?
# readme file? buildout should have this too.

import vobject

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
    when_over = models.DateTimeField(null=True)
    # KNESSET_TODO the end time of a committee meeting is not recorded anywhere,
    # so we are left to guess
    when_over_guessed = models.BooleanField(default=True)
    who = models.ManyToManyField(Person)
    # TODO - just randomly looking it seems to be wrong in some objects:
    # key 1957, contains repetition of the subject.
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

    def get_summary(self, length):
        """ this is used for the title of the event in the calendar view (icalendar) """
        return (self.what[:length - 3] + '...'
                 if len(self.what) >= length else self.what)

    @property
    def which(self):
        return self.which_object and unicode(self.which_object) or self.what

    def get_absolute_url(self):
        if self.which_object:
            return '%s#event-%d' % (self.which_object.get_absolute_url(), self.id)
        else:
            return '#'

    def add_vevent_to_ical(self, cal, summary_length):
        """
        adds itself as a vevent to @cal.
        cal should be a vobject.iCalendar
        """
        vevent = cal.add('vevent')
        vevent.add('dtstart').value = self.when
        if not self.when_over:
            # this can happen if you migrated so you have when_over but
            # have not run parse_future_committee_meetings yet.
            self.when_over = self.when + timedelta(hours=2)
            self.when_over_guessed = True
            self.save()
        # TODO: add `geo` to the Event model
        # FLOAT:FLOAT lon:lat, up to 6 digits, degrees.
        vevent.add('geo').value = '31.777067;35.205495'
        vevent.add('dtend').value = self.when_over
        summary = self.get_summary(summary_length)
        vevent.add('summary').value = summary
        vevent.add('location').value = self.where
        vevent.add('description').value = self.what
