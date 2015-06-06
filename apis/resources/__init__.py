'''
Here we collect the api resources. To add a new API endpoint create a tasypie
reource in an `api.py` file under the app and than import and resiter it here
'''
from tastypie.api import Api
from mks.api import MemberResource, PartyResource, MemberBillsResource, MemberAgendasResource
from video.api import VideoResource
from links.api import LinkResource
from laws.api import BillResource, LawResource, VoteResource, VoteActionResource
from agendas.api import AgendaResource, AgendaTodoResource
from committees.api import CommitteeResource, CommitteeMeetingResource, ProtocolPartResource
from auxiliary.api import PostResource, TagResource
from events.api import EventResource
from polyorg.api import CandidateListResource
from persons.api import PersonResource
from lobbyists.api import LobbyistsChangeResource, LobbyistResource, LobbyistCorporationResource

v2_api = Api(api_name='v2')

v2_api.register(MemberBillsResource())
v2_api.register(MemberAgendasResource())
v2_api.register(MemberResource())
v2_api.register(PartyResource())
v2_api.register(VideoResource())
v2_api.register(LinkResource())
v2_api.register(BillResource())
v2_api.register(VoteResource())
v2_api.register(VoteActionResource())
v2_api.register(LawResource())
v2_api.register(AgendaResource())
v2_api.register(AgendaTodoResource())
v2_api.register(CommitteeResource())
v2_api.register(CommitteeMeetingResource())
v2_api.register(ProtocolPartResource())
v2_api.register(PostResource())
v2_api.register(TagResource())
v2_api.register(EventResource())
v2_api.register(CandidateListResource())
v2_api.register(PersonResource())
v2_api.register(LobbyistsChangeResource())
v2_api.register(LobbyistResource())
v2_api.register(LobbyistCorporationResource())