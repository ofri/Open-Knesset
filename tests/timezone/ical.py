import web
import vobject
import datetime
from dateutil import zoneinfo

urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

def calendar(zone):
    tz = zoneinfo.gettz(zone)
    c = vobject.iCalendar()
    v = c.add('vevent')
    v.add('summary').value = 'test'
    v.add('description').value = 'testdesc'
    dtstart = datetime.datetime(year=2000, month=1, day=1, tzinfo=tz)
    v.add('dtstart').value = dtstart
    return c.serialize()

class hello:
    def GET(self, zone):
        return calendar(zone)

if __name__ == "__main__":
    app.run()
