from piston.handler import BaseHandler
from knesset.simple.models import Vote, Member, Party, Membership

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
            return Member.objects.all()

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
            return Vote.objects.all()

class PartyHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date')
    allowed_methods = ('GET',)
    model = Party
    def read(self, request, party_id=None):
        if party_id:
            return Party.objects.get(pk=party_id)
        else:
            return Party.objects.all()



