#encoding: utf-8
import datetime
from django.db.models.signals import post_save, pre_delete
from planet.models import Feed, Post
from actstream import action
from knesset.utils import cannonize, disable_for_loaddata
from knesset.agendas.models import AgendaVote
from knesset.agendas.models import Agenda
from knesset.links.models import Link, LinkType


@disable_for_loaddata
def record_agenda_ascription_action(sender, created, instance, **kwargs):
    if created:
        action.send(instance.agenda, verb='agenda ascribed',
                    description="agenda %s ascribed to vote %s" % (instance.agenda.name,instance.vote.title),
                    target = instance,
                    timestamp = datetime.datetime.now())
post_save.connect(record_agenda_ascription_action, sender=AgendaVote)


@disable_for_loaddata
def record_agenda_removal_action(sender, instance, **kwargs):
    action.send(instance.agenda, verb='agenda removed',
                description="agenda %s removed from vote %s" % (instance.agenda.name,instance.vote.title),
                target = instance,
                timestamp = datetime.datetime.now())
pre_delete.connect(record_agenda_removal_action, sender=AgendaVote)
