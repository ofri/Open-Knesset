from apis.resources.base import BaseResource
from models import Role

class RoleResource(BaseResource):
    ''' Role API
    '''
    class Meta(BaseResource.Meta):
        queryset = Role.objects.all()
        allowed_methods = ['get']
        excludes = ["id"]
        include_resource_uri = False
