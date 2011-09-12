import os, csv
from django.core.management.base import NoArgsCommand
from django.conf import settings

from knesset.mks.models import Member,Party
from knesset.laws.models import Vote,VoteAction
from knesset.agendas.models import Agenda, AgendaVote

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        mks = Member.objects.order_by('current_party').values('id','name','current_party')
        for agenda in Agenda.objects.all():
            f = open(os.path.join(settings.DATA_ROOT, 'agenda_%d.csv' %
                                  agenda.id), 'wt')
            csv_writer = csv.writer(f)
            header = []
            header.append('Vote id')
            header.append('Vote title')
            header.append('Score')
            for mk in mks:
                header.append('%s %d' % (mk['name'].encode('utf8'), mk['id']))
            csv_writer.writerow(header)

            for agenda_vote in AgendaVote.objects.filter(agenda=agenda):
                row = []
                row.append(agenda_vote.vote.id)
                row.append(agenda_vote.vote.title.encode('utf8'))
                row.append(agenda_vote.score)
                mks_for = agenda_vote.vote.get_voters_id('for')
                mks_against = agenda_vote.vote.get_voters_id('against')
                for mk in mks:
                    if mk['id'] in mks_for:
                        row.append(1)
                    elif mk['id'] in mks_against:
                        row.append(-1)
                    else:
                        row.append(0)
                csv_writer.writerow(row)
            f.close()







