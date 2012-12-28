# encoding: utf-8
import logging, csv
from collections import namedtuple
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger("open-knesset.polyorg.import_candidatelist")

CandidateTuple = namedtuple('CandidateTuple', ['comments', 'mqg', 'manifest_url', 'party_website', 'image_url', 'id','ordinal','member','letters','party'])

class Command(BaseCommand):
    def handle(self, *args, **options):
        for csv_file in args:
            self.stdout.write('Import from %s\n' % (csv_file))
            #logger.debug('Import from %s' % (csv_file))
            #with open(csv_file, 'rb') as cf:
            #    reader = csv.reader(cf) #, delimiter=' ', quotechar='|')
            idx = 0
            for cnd in map(CandidateTuple._make, csv.reader(open(csv_file, "rb"))):
                if idx > 0:
                    # a record, not list of columns
                    if cnd.id:
                        print '%s has ID %s' % (cnd.member, cnd.id)
                        
                    else:
                        print '%s has no ID' % (cnd.member)
                idx += 1
                if idx > 12:
                    break
