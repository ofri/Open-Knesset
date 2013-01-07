# encoding: utf-8

from django.core.management.base import NoArgsCommand
from optparse import make_option
from simple.management.commands.parse_plenum_protocols_subcommands.download import Download
from simple.management.commands.parse_plenum_protocols_subcommands.parse import Parse

class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--download',action='store_true',dest='download',
            help="download the latest protocols from http://www.knesset.gov.il/plenum/heb/plenum_queue.aspx"),
        make_option('--robots',action='store_true',dest='robots',
            help="download from the knesset's robots.txt file (only useful with the --download option)"),
        make_option('--parse',action='store_true',dest='parse',
            help="parse the downloaded protocols into machine-readable format"),
        make_option('--updatedb',action='store_true',dest='object-type',
            help="update the database with the parsed protocols"),
    )

    def handle_noargs(self, **options):
        if options.get('download',False):
            Download(options.get('verbosity',1),options.get('robots',False))
        elif options.get('parse',False):
            Parse(options.get('verbosity',1))
        else:
            print "invalid option, try --help"

