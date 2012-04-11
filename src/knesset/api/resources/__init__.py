
from tastypie.api import Api
from Member import MemberResource
from Party import PartyResource
from Video import VideoResource

v2_api = Api(api_name='v2')
v2_api.register(MemberResource())
v2_api.register(PartyResource())
v2_api.register(VideoResource())
