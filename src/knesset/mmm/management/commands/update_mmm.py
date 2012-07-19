from django.core.management.base import NoArgsCommand, CommandError
from knesset.mmm.models import Document
import simplejson


class Command(NoArgsCommand):
    help = "Updating mmm table"
    
    def handle_noargs(self, **options):
        
        try:
            url = DATA_ROOT + 'mmm_matches.json'
            json = open(url, 'r')
        except IOError as e:
            raise CommandError('[Errno - {0}]: {1} {2}'.format(e.errno, e.strerror, url))
        
        Document.objects.from_json(json)