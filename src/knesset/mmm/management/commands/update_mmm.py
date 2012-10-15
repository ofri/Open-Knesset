from datetime import datetime

from django.core.management.base import NoArgsCommand, CommandError
from django.utils import simplejson

from knesset.mmm.models import Document
from knesset.settings import DATA_ROOT


def parse_json(str):
    """ receives fp.read result, loads/parses and returns a list of dictionaries """

    result = simplejson.loads(str)

    # translating date strings to datetime objects
    for o in result:
        o['date'] = datetime.strptime(o['date'], '%d/%m/%Y').date()

    return result

def combine_jsons(matches, mmm):
    """
    params:
      matches - fp.read() result of matches.json
      mmm - fp.read() result of mmm.json

    returns:
      json - list of matches objects with added authors from mmm.
    """
    # parse matches.json and mmm.json to python obj's
    json = parse_json(matches)
    mmm = simplejson.loads(mmm)

    # create a dictionary of urls - authors
    authors = dict((o['url'], ', '.join(o['authors'])) for o in mmm)

    # modifying matches to include author field
    for i in json:
        i['author'] = authors[i['url']]

    return json

class Command(NoArgsCommand):
    help = "Updating mmm table"


    def handle_noargs(self, **options):
        json1 = open(DATA_ROOT + 'matches.json', 'rt').read()
        json2 = open(DATA_ROOT + 'mmm.json', 'rt').read()
        Document.objects.from_json(combine_jsons(json1, json2))