from datetime import datetime
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
    fields = ('id', 'url', 'name','party', 'img_url', 'votes_count', 'votes_per_month', 'service_time', 'discipline','average_weekly_presence')
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
        vote_id = None
        if 'vote_id' in kwargs:
            vote_id = kwargs['vote_id']
        if vote_id:
            tags_ids = TaggedItem.objects.filter(object_id=vote_id).values_list('tag', flat=True)
            return Tag.objects.filter(id__in=tags_ids)

        return Tag.objects.all().order_by('name')
    
    @classmethod
    def number_of_items(self, tag):
        return tag.items.count()


