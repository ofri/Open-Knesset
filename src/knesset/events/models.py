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

    @property
    def location(self):
        """ location of vevent in calendar view """
        if self.which_object:
            c = self.which_object
            # Today it is only committee
            return c.name
        return None

    @property
    def summary(self):
        """ this is used for the title of the event in the calendar view (icalendar) """
        topic = self.what[:30] + '...' if len(self.what) >= 30 else self.what
        return topic

    @property
    def which(self):
        return self.which_objects and unicode(self.which_object) or self.what

    def add_vevent_to_ical(self, cal):
        """
        adds itself as a vevent to @cal.
        cal should be a vobject.iCalendar
        """
        vevent = cal.add('vevent')
        vevent.add('dtstart').value = self.when
        summary = self.what
        if not self.when_over:
            # this can happen if you migrated so you have when_over but
            # have not run parse_future_committee_meetings yet.
            self.when_over = self.when + timedelta(hours=2)
            self.when_over_guessed = True
            self.save()
        if self.when_over_guessed:
            summary = u'ATTENTION: The end date is just projected, not available on knesset.gov. Be advised!\n\n' + summary
        # FLOAT:FLOAT lon:lat, up to 6 digits, degrees.
        vevent.add('geo').value = '31.777067;35.205495'
        vevent.add('dtend').value = self.when_over
        vevent.add('summary').value = self.summary
        location = self.location
        if location:
            vevent.add('location').value = location
        vevent.add('description').value = self.what
