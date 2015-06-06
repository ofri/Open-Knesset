from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.fields import ToOneField, DictField
from apis.resources.base import BaseResource
from models import LobbyistsChange, Lobbyist, LobbyistCorporation
from persons.api import PersonResource


class LobbyistResource(BaseResource):
    person = ToOneField(PersonResource, 'person')
    data = DictField('cached_data')

    class Meta(BaseResource.Meta):
        queryset = Lobbyist.objects.all()


class LobbyistCorporationResource(BaseResource):
    data = DictField('cached_data')

    class Meta(BaseResource.Meta):
        queryset = LobbyistCorporation.objects.all()


class LobbyistsChangeResource(BaseResource):
    content_object = GenericForeignKeyField({
        Lobbyist: LobbyistResource,
        LobbyistCorporation: LobbyistCorporationResource
    }, 'content_object')

    class Meta(BaseResource.Meta):
        queryset = LobbyistsChange.objects.all()
        allowed_methods = ['get']
