from piston.handler import BaseHandler
from knesset.simple.models import Vote, Member, Membership

class MemberHandler(BaseHandler):
    fields = ('id', 'name', 'start_date', 'end_date',
              'membership',
             )
    allowed_methods = ('GET',)
    model = Member
    def read(self, request, member_id):
        member = Member.objects.get(pk=member_id)
        return member

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
    def read(self, request, vote_id):
        vote = Vote.objects.get(pk=vote_id)
        return vote


