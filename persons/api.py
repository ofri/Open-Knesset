from django.contrib.auth.models import User
from tastypie.constants import ALL, ALL_WITH_RELATIONS
import tastypie.fields as fields

from apis.resources.base import BaseResource
from .models import *

class ExternalRelationResource(BaseResource):
    with_person = fields.ToOneField('persons.api.PersonResource', 'with_person', null=True)
    class Meta(BaseResource.Meta):
        queryset = ExternalRelation.objects.all()
        allowed_methods = ['get']
        excludes = ["id"]
        include_resource_uri = False
        filtering = {
                'source': ALL,
                'relationship': ALL,
                'with_person': ALL_WITH_RELATIONS,
                }

class ExternalInfoResource(BaseResource):
    class Meta(BaseResource.Meta):
        queryset = ExternalInfo.objects.all()
        allowed_methods = ['get']
        excludes = ["id"]
        include_resource_uri = False
        filtering = {
                'source': ALL,
                'key': ALL,
                'person': ALL_WITH_RELATIONS,
                }

class RoleResource(BaseResource):
    ''' Role API
    '''
    class Meta(BaseResource.Meta):
        queryset = Role.objects.all()
        allowed_methods = ['get']
        excludes = ["id"]
        include_resource_uri = False
        filtering = {
                'org': ALL,
                'text': ALL,
                }

class PersonResource(BaseResource):

    roles = fields.ToManyField(RoleResource, 'roles', full=True)
    mk = fields.ToOneField('mks.api.MemberResource', 'mk', null=True, full=True)
    relations = fields.ToManyField(ExternalRelationResource, 'external_relation', full=True)
    external_info = fields.ToManyField(ExternalInfoResource, 'external_info', full=True)

    class Meta(BaseResource.Meta):
        queryset = Person.objects.all()
        allowed_methods = ['get']
        filtering = {
                'roles': ALL_WITH_RELATIONS,
                'relations': ALL_WITH_RELATIONS,
                'external_info': ALL_WITH_RELATIONS,
                }

    def get_object_list(self, request):
        persons = super(PersonResource, self).get_object_list(request)
        user_id = request.GET.get('user_id', '')
        if len(user_id) > 0:
            persons = persons.filter(user__id=user_id)
        return persons
