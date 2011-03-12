from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.db.models import Max

from knesset.simple.management.commands import parse_laws
from knesset.laws.models import GovProposal

def parse_gov_laws(use_last_booklet):
    booklet = 0
    if use_last_booklet:
        booklet = GovProposal.objects.aggregate(Max('booklet_number')).values()[0]
    parser = parse_laws.ParseGovLaws(booklet)
    parser.parse_gov_laws()

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--forceupdate', action='store_true', dest='forceupdate',
            help="forced update for gov bills, will download all pdfs and update Bills"),
        make_option('--pdf', action='store', dest='pdf', default=None,
            help="forced update for gov bills, will download all pdfs and update Bills"),)

    help = "Give information on government bills (pdfs)"

    def handle_noargs(self, **options):
        forceupdate = options.get('forceupdate', False)
        pdf = options.get('pdf')
        if pdf:
            parse_laws.ParseGovLaws(0).update_single_bill(pdf)
            print "updated: %s" % GovProposal.objects.filter(source_url=pdf)[0].get_absolute_url()
        else:
            parse_gov_laws(not forceupdate)
