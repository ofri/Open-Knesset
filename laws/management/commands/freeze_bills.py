from __future__ import print_function

from django.core.management.base import BaseCommand
from optparse import make_option

from laws.models import Bill
from laws.vote_choices import BILL_STAGE_CHOICES
from mks.models import Knesset


class Command(BaseCommand):

    help = "Freeze bills staged in previous knessets"

    option_list = BaseCommand.option_list + (
        make_option(
            '-n', action='store_true', dest="dryrun", default=False,
            help='Dry run, changes nothing in the db, just display results'
        ),
    )

    def handle(self, *args, **options):

        start_date = Knesset.objects.current_knesset().start_date

        valid_stages = [key for (key, val) in BILL_STAGE_CHOICES
                        if key.isnumeric() and 1 < int(key) < 6]

        bills = Bill.objects.filter(stage_date__lte=start_date,
                                    stage__in=valid_stages)

        total = Bill.objects.count()
        found = bills.count()

        msg = "Found {0} bills of {1} in stages {2} and dated before {3}"
        print(msg.format(found, total, u','.join(valid_stages), start_date))

        if options['dryrun']:
            print("Not updating the db, dry run was specified")
        else:
            print('Settings {0} bills stage to u"0"'.format(found))
            bills.update(stage=u'0')
