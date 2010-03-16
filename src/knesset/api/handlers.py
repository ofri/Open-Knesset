from datetime import datetime
from piston.handler import BaseHandler
from knesset.mks.models import Member, Party, Membership
from knesset.laws.models import Vote, VoteAction

DEFAULT_PAGE_LEN = 20
def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page*num:(page+1)*num]
    return qs

class MemberHandler(BaseHandler):
    fields = ('url', 'name', 
              'member',)
    allowed_methods = ('GET',)
    model = Member
    qs = Membership.objects.all()
    def read(self, request, **kwargs):
        if member_id in kwargs:
            qs = self.qs.filter(pk=kwargs[member_id])
        else:
            year = request.GET.get('year', None)
            if year:
                qs = self.qs.filter(end_date__gte=yearstart(year))
        return qs

    @classmethod
    def url (self, member):
        return member.get_absolute_url()

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
              'summary',
              'for_votes', 'agains_votes' , 'abstain_votes' , 'didnt_vote' ,
              'topics_for', 'topics_against',
              'full_text_url',
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
    def abstain_votes(self, vote):
        return vote.get_voters_id('abstain')

    @classmethod
    def didnt_vote(self, vote):
        return vote.get_voters_id('no-vote')

class PartyHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date')
    allowed_methods = ('GET',)
    model = Party
    
    def read(self, request, party_id=None):
        if party_id:
            return Party.objects.filter(pk=party_id)
        else:
            return Party.objects.all()
