from django.core.management.base import NoArgsCommand
from knesset.mmm.models import Document
import simplejson


class Command(NoArgsCommand):
    help = "Updating mmm table"
    
    def handle_noargs(self, **options):
        
        json = open(DATA_ROOT + 'mmm_matches.json')
        
        Document.objects.from_json(json)