from __future__ import division

from django.core.management.base import NoArgsCommand
from django.db import transaction
from django.utils.timezone import now

from agendas.models import SummaryAgenda,AgendaVote

class Command(NoArgsCommand):

    @transaction.commit_manually
    def handle_noargs(self, **options):
        print('Deleting existing summary objects')
        SummaryAgenda.objects.all().delete()
        numAgendaVotes = AgendaVote.objects.count()
        print('Summary agenda objects deleted, recalculating for %d votes' % \
                    numAgendaVotes)
        i=0
        lastReportedPct = 0.0
        for agendavote in AgendaVote.objects.all():
            pct = i/numAgendaVotes
            if (i/numAgendaVotes) - lastReportedPct >= 0.01:
                print('%s: Completed %d of %d votes (%d%%)' % (str(now()),i,numAgendaVotes,100*pct))
                lastReportedPct = i/numAgendaVotes
                transaction.commit()
            agendavote.update_monthly_counters()
            i+=1
        transaction.commit()
        print('Completed recalculation of agenda votes')
