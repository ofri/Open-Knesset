from piston.handler import BaseHandler
from knesset.simple.models import Vote

class VoteHandler(BaseHandler):
    # fields = ('for', 'against', 'abstain')
    fields = ('id', 'time', 'ForVotesCount', 'AgainstVotesCount', 
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


