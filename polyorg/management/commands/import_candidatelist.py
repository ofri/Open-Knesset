# encoding: utf-8
import logging, csv, itertools
from collections import namedtuple
from django.core.management.base import BaseCommand
from polyorg.models import Candidate
from polyorg.models import CandidateList
from mks.models import Member
from persons.models import Person
from django.db import transaction

logger = logging.getLogger("open-knesset.polyorg.import_candidatelist")

CandidateTuple = namedtuple('CandidateTuple', ['comments', 'wikipedia', 'mqg', 'manifest_url', 'party_website', 'image_url', 'mk_id', 'ordinal', 'name', 'ballot', 'list'])

class Command(BaseCommand):
    def _list_by_cnd(self, cnd):
        ls = CandidateList.objects.filter(name__exact = cnd.list)
        if ls:
            return ls[0]
        clist = CandidateList.objects.create(name = cnd.list, ballot = cnd.ballot)
        return clist

    def _person_by_cnd(self, cnd):
        persons = list(Person.objects.filter(name__exact = cnd.name))
        if cnd.mk_id:
            persons = list(Person.objects.filter(mk__id = cnd.mk_id)) + persons
        if persons:
            return persons[0]
        return Person.objects.create(name = cnd.name)

    @transaction.commit_on_success()
    def handle(self, *args, **options):
        # For each candidate:
        #    Build a Candidate object
        for csv_file in args:
            self.stdout.write('Import from %s\n' % (csv_file))
            for cnd in itertools.islice(map(CandidateTuple._make, csv.reader(open(csv_file, "rb"))), 2, None):
                clist = self._list_by_cnd(cnd)
                person = self._person_by_cnd(cnd)
                candidate = Candidate.objects.create(candidates_list = clist, person = person, ordinal = cnd.ordinal)
