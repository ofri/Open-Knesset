
from django.conf.urls.defaults import patterns, url, include
from tastypie.api import Api
from knesset.api.resources import MemberResource

v2_api = Api(api_name='v2')
v2_api.register(MemberResource())
