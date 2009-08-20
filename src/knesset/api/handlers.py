from piston.handler import BaseHandler
from knesset.simple.models import Vote, Member, Party, Membership

def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page*num:(page+1)*num]
    return qs

class MemberHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date',
              'membership',
             )
    allowed_methods = ('GET',)
    model = Member
    def read(self, request, member_id=None):
        if member_id:
            return Member.objects.get(pk=member_id)
        else:
            qs = Member.objects.all().order_by('-end_date', 'name')
            return limit_by_request(qs, request)

    @classmethod
    def membership (self, member):
        qs = Membership.objects.filter(member=member)
        return qs.values('start_date', 'end_date', 'party_id')

class VoteHandler(BaseHandler):
    # fields = ('for', 'against', 'abstain')
    fields = ('id', 'title', 'time', 'ForVotesCount', 'AgainstVotesCount',
              ('voted_for' , ('member', ('id'))),
              ('voted_against' , ('member', ('id'))),
              ('voted_abstain' , ('member', ('id'))),
              ('didn_vote' , ('member', ('id'))),
              'topics_for',
              'topics_against',
             )
    allowed_methods = ('GET',)
    model = Vote
    def read(self, request, vote_id=None):
        if vote_id:
            return Vote.objects.get(pk=vote_id)
        else:
            qs = Vote.objects.all()
            return limit_by_request(qs, request)

class PartyHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date')
    allowed_methods = ('GET',)
    model = Party
    def read(self, request, party_id=None):
        if party_id:
            return Party.objects.get(pk=party_id)
        else:
            qs = Party.objects.all()
            return limit_by_request(qs, request)



