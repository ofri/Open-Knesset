from datetime import datetime
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models import Count
from piston.handler import BaseHandler
from piston.utils import rc
from knesset.mks.models import Member, Party, Membership
from knesset.laws.models import Vote, VoteAction
from tagging.models import Tag, TaggedItem

DEFAULT_PAGE_LEN = 20
def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page*num:(page+1)*num]
    return qs

class MemberHandler(BaseHandler):
    fields = ('id', 'url', 'name','party', 'img_url', 'votes_count', 'votes_per_month', 'service_time', 'discipline','average_weekly_presence', 'committee_meetings_per_month','bills_proposed','bills_passed_pre_vote','bills_passed_first_vote','bills_approved', 'roles', 'average_weekly_presence_rank', 'committees', )
    allowed_methods = ('GET')
    model = Member
    qs = Member.objects.all()

    @classmethod
    def url (self, member):
        return member.get_absolute_url()

    @classmethod
    def party (self, member):
        return member.current_party.name

    @classmethod
    def votes_count (self, member):
        return member.voting_statistics.votes_count()

    @classmethod
    def votes_per_month (self, member):
        return round(member.voting_statistics.average_votes_per_month(),1)

    @classmethod
    def service_time (self, member):
        return member.service_time()
    
    @classmethod
    def discipline (self, member):
        x = member.voting_statistics.discipline()
        if x:
            return round(x,2)
        else:
            return None

    @classmethod
    def bills_proposed(self, member):
        return member.bills.count()

    @classmethod
    def bills_passed_pre_vote(self, member):
        return member.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()

    @classmethod
    def bills_passed_first_vote(self, member):
        return member.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()

    @classmethod
    def bills_approved(self, member):
        return member.bills.filter(stage='6').count()

    @classmethod
    def roles (self, member):
        return u'Unknown'

    @classmethod
    def average_weekly_presence_rank (self, member):
        ''' Calculate the distribution of presence and place the user on a 5 level scale '''
        SCALE = 5

        avg = member.average_weekly_presence()
        if not avg:
            return None

        presence_list = cache.get('average_presence_list')
        if not presence_list:
            presence_list = sorted(map(lambda member: member.average_weekly_presence(), Member.objects.all()))
            cache.set('average_presence_list', presence_list, 60*60*24)

        rel_location= cache.get('average_presence_location_%d' % member.id)
        if not rel_location:
            # Find member's relative location in the list
            for pos, item in enumerate(presence_list):
                if item > avg:
                    location = pos
                    break
            else:
                location = len(presence_list)

            rel_location = location / (len(presence_list) / SCALE)
            cache.set('average_presence_location_%d' % member.id, rel_location, 60*60*24)

        return rel_location

    @classmethod
    def committees (self, member):
        temp_list = member.committee_meetings.values("committee", "committee__name").annotate(Count("id")).order_by('-id__count')[:5]
        return (map(lambda item: (item['id__count'], item['committee__name'], reverse('committee-meeting', args=[item['committee']])), temp_list))

    @classmethod
    def member (self, member):
        qs = self.qs.filter(member=member)
        return map(lambda o: dict(url=o.party.get_absolute_url(),
                     name=o.party.name,
                     since=o.start_date,
                     until=o.end_date,
                     ), qs)

class VoteHandler(BaseHandler):
    fields = ('url', 'title', 'time', 
              'summary','full_text',
              'for_votes', 'against_votes' , 'abstain_votes' , 'didnt_vote' ,
             )
    exclude = ('member')
    allowed_methods = ('GET',)
    model = Vote
    qs = Vote.objects.all()

    def read(self, request, **kwargs):
        ''' returns a vote or a list of votes '''
        qs = self.qs

        if 'id' in kwargs:
            return super(VoteHandler, self).read(request, **kwargs)

        type = request.GET.get('type', None)
        order = request.GET.get('order', None)
        days_back = request.GET.get('days_back', None)
        page_len = request.GET.get('page_len', DEFAULT_PAGE_LEN)
        page_num=request.GET.get('page_num', 0)

        if type:
            qs = qs.filter(title__contains=type)
        if days_back:
            qs = qs.since(days=days_back)
        if order:
            qs = qs.sort(by=order)
        return qs[page_len*page_num:page_len*(page_num +1)]

    @classmethod
    def url(self, vote):
        return vote.get_absolute_url()

    @classmethod
    def for_votes(self, vote):
        return vote.get_voters_id('for')

    @classmethod
    def against_votes(self, vote):
        return vote.get_voters_id('against')

    @classmethod
    def abstain_votes(self, vote):
        return vote.get_voters_id('abstain')

    @classmethod
    def didnt_vote(self, vote):
        return vote.get_voters_id('no-vote')

class PartyHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date')
    allowed_methods = ('GET',)
    model = Party
    
    def read(self, request, id=None):
        if id:
            return Party.objects.filter(pk=id)
        else:
            return Party.objects.all()

class TagHandler(BaseHandler):
    fields = ('id', 'name', 'number_of_items')
    allowed_methods = ('GET',)
    model = Tag
    
    def read(self, request, **kwargs):
        id = None
        if 'id' in kwargs:
            id = kwargs['id']        
        if id:
            return Tag.objects.filter(pk=id)
        object_id = None
        ctype = None
        if 'object_id' in kwargs and 'object_type' in kwargs:
            object_id = kwargs['object_id']
            try:
                ctype = ContentType.objects.get(model=kwargs['object_type'])
            except ContentType.DoesNotExist:
                pass
        if object_id and ctype:
            tags_ids = TaggedItem.objects.filter(object_id=object_id).filter(content_type=ctype).values_list('tag', flat=True)
            return Tag.objects.filter(id__in=tags_ids)

        return Tag.objects.usage_for_model(Vote)
    
    @classmethod
    def number_of_items(self, tag):
        return tag.items.count()


