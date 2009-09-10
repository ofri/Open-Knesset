from datetime import datetime
from piston.handler import BaseHandler
from knesset.mks.models import Member, Party, Membership
from knesset.laws.models import Vote, VoteAction
from knesset.utils import yearstart, yearend

def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page*num:(page+1)*num]
    return qs

class MemberHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date',
              'membership',)
    allowed_methods = ('GET',)
    model = Member
    def read(self, request, member_id=None):
        if member_id:
            qs = Member.objects.filter(pk=member_id)
        else:
            year = request.GET.get('year', -1)
            if year == -1:
                year = datetime.now().year
            qs = Member.objects.filter(end_date__gte=yearstart(2009))
        return qs

    @classmethod
    def membership (self, member):
        qs = Membership.objects.filter(member=member)
        return [dict(since=o.start_date, until=o.end_date,
                     id=o.party.uri_template) for o in qs]

class VoteDetailsHandler(BaseHandler):
    # fields = ('for', 'against', 'abstain')
    fields = ('id', 'title', 'time', 'for_votes_counts', 'against_votes_counts',
              'member_uri_template', 
              'voted_for',
              'voted_against' ,
              'voted_abstain' ,
              'didnt_vote' ,
              'topics_for',
              'topics_against',
              'summary',
              'full_text_url',
             )
    allowed_methods = ('GET',)
    model = Vote
    def read(self, request, vote_id):
        return Vote.objects.filter(pk=vote_id)

    @classmethod
    def member_uri_template(self, vote):
        # TODO: needs Drying - use django's url resolver
        return "/member/{id}/htmldiv/" 

    @classmethod
    def voted_for(self, vote):
        return vote.get_voters_id('for')

    @classmethod
    def voted_against(self, vote):
        return vote.get_voters_id('against')

    @classmethod
    def voted_abstain(self, vote):
        return vote.get_voters_id('abstain')

    @classmethod
    def didnt_vote(self, vote):
        return vote.get_voters_id('no-vote')

class VoteHandler(BaseHandler):
    # fields = ('for', 'against', 'abstain')
    fields = ('id', 'title', 'time', 'for_votes_count', 'against_vote_count',
              'topics_for',
              'topics_against',
             )
    allowed_methods = ('GET',)
    model = Vote
    def read(self, request):
        qs = Vote.objects.all().order_by('-time')
        return limit_by_request(qs, request)

class PartyHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date')
    allowed_methods = ('GET',)
    model = Party
    def read(self, request, party_id=None):
        if party_id:
            return Party.objects.get(pk=party_id)
        else:
            return Party.objects.all()
