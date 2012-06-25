'''
Here we collect the api resources. To add a new API endpoint create a tasypie
reource in an `api.py` file under the app and than import and resiter it here
'''
from tastypie.api import Api
from mks.api import MemberResource, PartyResource, MemberBillsResource, MemberAgendasResource
from video.api import VideoResource
from links.api import LinkResource
from laws.api import BillResource, LawResource
from agendas.api import AgendaResource, AgendaTodoResource

v2_api = Api(api_name='v2')

v2_api.register(MemberBillsResource())
v2_api.register(MemberAgendasResource())
v2_api.register(MemberResource())
v2_api.register(PartyResource())
v2_api.register(VideoResource())
v2_api.register(LinkResource())
v2_api.register(BillResource())
v2_api.register(LawResource())
v2_api.register(AgendaResource())
v2_api.register(AgendaTodoResource())
