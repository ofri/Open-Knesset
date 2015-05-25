# encoding: utf-8

from django.core.management.base import NoArgsCommand
from optparse import make_option
from committees.models import Committee
from datetime import datetime, timedelta


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--all',action='store_true',dest='all',
            help="process all plenum protocols (instead of just the latest)"),
        make_option('--reparse',action='store_true',dest='reparse',
            help="also redownload and reparse the protocol text")
    )

    latest_days = 30

    def handle_noargs(self, **options):
        plenum = Committee.objects.get(name='Plenum')
        if options.get('all', False):
            qs = plenum.meetings.all()
        else:
            qs = plenum.meetings.filter(date__gte=datetime.now()-timedelta(days=self.latest_days))
        for meeting in qs:
            if int(options.get('verbosity', '1')) > 1:
                print 'meeting %s'%meeting.pk
            if options.get('reparse', False):
                meeting.reparse_plenum_protocol()
            meeting.plenum_link_votes()
