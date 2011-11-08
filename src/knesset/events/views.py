# Create your views here.

from datetime import datetime

import vobject

from django.http import HttpResponse
from models import Event

def icalendar(request, future_only=False):
    """
    return a single icalendar file, optionally for a subset of the events.
    """
    cal = vobject.iCalendar()
    now = datetime.now()
    for e in Event.objects.all():
        # TODO - use a proper query once I recall the syntax (actually the implementation
        # of is_future makes this query pretty bad, since it will execute multiple times - to
        # do this properly I need some sort of select * from table where start_date > $now,
        # then now is only calculated once, and this should be log(N) time (assuming an ordered
        # index on start_date)
        if future_only and e.when <= now:
            continue
        e.add_vevent_to_ical(cal)
    return HttpResponse(cal.serialize())
