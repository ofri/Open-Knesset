import os, csv
from operator import attrgetter
from django.core.management.base import NoArgsCommand
from django.conf import settings

from tagging.models import Tag, TaggedItem

from mks.models import Member,Party
from laws.models import Vote,VoteAction,Bill

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        mks = Member.objects.order_by('current_party__is_coalition','current_party__name')\
                .values('id','name','current_party__name')
        f = open(os.path.join(settings.DATA_ROOT, 'mks.csv'), 'wt')
        mk_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        for mk in mks:
            row = [mk['id'],
                   '%s' % mk['name'].encode('utf8'),
                   '%s' % mk['current_party__name'].encode('utf8')]
            mk_writer.writerow(row)
        f.close()

        vote_tags = Tag.objects.usage_for_model(Vote)
        bill_tags = Tag.objects.usage_for_model(Bill)
        all_tags = list(set(vote_tags).union(bill_tags))
        all_tags.sort(key=attrgetter('name'))

        f = open(os.path.join(settings.DATA_ROOT, 'votes_mks.csv'), 'wt')
        mk_writer = csv.writer(f)
        header = ['Vote id', 'Vote time', 'Vote name']
        for mk in mks:
            header.append(mk['id'])
        mk_writer.writerow(header)

        f2 = open(os.path.join(settings.DATA_ROOT, 'tags.csv'), 'wt')
        tag_writer = csv.writer(f2)
        header = ['Tag id', 'Tag Name']
        tag_writer.writerow(header)
        for tag in all_tags:
            tag_writer.writerow([tag.id, tag.name.encode('utf8')])
        f2.close()

        f2 = open(os.path.join(settings.DATA_ROOT, 'votes_tags.csv'), 'wt')
        tag_writer = csv.writer(f2)
        header = ['Vote id', 'Vote time', 'Vote name']
        for tag in all_tags:
            header.append(tag.id)
        tag_writer.writerow(header)

        for vote in Vote.objects.iterator():
            row = [vote.id, vote.time, vote.title.encode('utf8')]
            mks_for = vote.get_voters_id('for')
            mks_against = vote.get_voters_id('against')
            for mk in mks:
                if mk['id'] in mks_for:
                    row.append(1)
                elif mk['id'] in mks_against:
                    row.append(-1)
                else:
                    row.append(0)
            mk_writer.writerow(row)

            row = [vote.id, vote.time, vote.title.encode('utf8')]
            tags = vote.tags
            for tag in all_tags:
                if tag in tags:
                    row.append(1)
                else:
                    row.append(0)
            tag_writer.writerow(row)

        f.close()
        f2.close()







