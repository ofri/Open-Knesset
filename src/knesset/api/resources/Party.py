from tastypie.resources import ModelResource
from knesset.mks.models import Party
from knesset.api.resources.Base import BaseResource

class PartyResource(BaseResource):
    
    class Meta:
        queryset = Party.objects.all()
        allowed_methods = ['get']