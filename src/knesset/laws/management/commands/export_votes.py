import os, csv
from django.core.management.base import NoArgsCommand
from django.conf import settings

from knesset.mks.models import Member,Party
from knesset.laws.models import Vote,VoteAction

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        mks = Member.objects.order_by('current_party').values('id','name','current_party')
        f = open(os.path.join(settings.DATA_ROOT, 'votes_mks.csv'), 'wt')
        csv_writer = csv.writer(f)
        header = []
        header.append('Vote id')
        header.append('Vote time')
        header.append('Vote name')
        for mk in mks:
            header.append(mk['id'])
        csv_writer.writerow(header)

        for vote in Vote.objects.all():
            row = []
            row.append(vote.id)
            row.append(vote.time)
            row.append(vote.title.encode('utf8'))
            mks_for = vote.get_voters_id('for')
            mks_against = vote.get_voters_id('against')
            for mk in mks:
                if mk['id'] in mks_for:
                    row.append(1)
                elif mk['id'] in mks_against:
                    row.append(-1)
                else:
                    row.append(0)
            csv_writer.writerow(row)
        f.close()







