from datetime import datetime

from django.core.management.base import NoArgsCommand, CommandError
from django.utils import simplejson

from knesset.mmm.models import Document
from knesset.settings import DATA_ROOT


def parse_json(fp):
    """ receives fp from data folder, loads/parses and returns a list of dictionaries """

    result = simplejson.load(fp)

    # modifying the data to be suitable for use
    for o in result:
    #        o['candidates'] = re.sub(r"\s+", r" " , " ".join(o['candidates']))
        o['date'] = datetime.strptime(o['date'], '%d/%m/%Y')

    return result

class Command(NoArgsCommand):
    help = "Updating mmm table"

    def handle_noargs(self, **options):

        # parse matches.json and mmm.json to python obj's
        json = parse_json(open(DATA_ROOT + 'matches.json'))
        mmm = parse_json(open(DATA_ROOT + 'mmm.json'))

        # create a dictionary of urls - authors
        authors = dict((o['url'], ', '.join(o['authors'])) for o in mmm)

        # modifying matches to include author field
        for i in json:
            i['author'] = authors[i['url']]

        Document.objects.from_json(json)