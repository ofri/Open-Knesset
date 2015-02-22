# -*- coding: utf-8 -*-
import sys
import re
import logging
from optparse import make_option
import csv
import codecs
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from persons.models import Person, PersonAlias, Role

logger = logging.getLogger("open-knesset.import_persons_csv")

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--save',
            action='store_true',
            dest='save',
            default=True,
            help='store the info in the DB'),
        make_option('-i',
            dest='input',
            default=False,
            help='name of an input file'),
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='delete the data in the csv from the db'),
        make_option('--source',
            dest='source',
            default=False,
            help='delete the data in the csv from the db'),
        )
    help = 'process a csv with persons data from standard input'

    def get_person(self, text):
        name, sep, titles = text.partition('/')
        titles = titles.split(',')
        p = Person.objects.get_by_name(name, create=True)
        for t in titles:
            p.titles.get_or_create(name=t)
        return p

    def handle(self, *args, **options):
        if options['save']:
            if options['input']:
                f = codecs.open(options['input'], "r", "utf-8")
            else:
                f = sys.stdin
            for line in csv.DictReader(f):
                p = Person.objects.get_by_name(line['name'], create=True)
                for key,value in line.items():
                    parts = key.split('_')
                    if parts[0] == "person":
                        if value:
                            other = self.get_person(value)
                            new, created = p.external_relation.get_or_create(source=options['source'],
                                relationship=_(parts[1]),
                                with_person=other,
                            )
                            self.stdout.write(unicode(new))
                    else:
                        ei, created = p.external_info.get_or_create(source=options['source'],
                            key= _(key), defaults=dict(value=value))
                        if not created:
                            ei.value=value,
                            ei.save()
                        print key, ':', value
                        continue
