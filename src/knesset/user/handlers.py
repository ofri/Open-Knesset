from datetime import datetime
from piston.handler import BaseHandler
from piston.utils import rc
from django.contrib.auth.models import User
from knesset.mks.models import Member

class UserHandler(BaseHandler):
    fields = ('username')
    allowed_methods = ('GET','DELETE', 'PUT')
    model = User
    qs = User.objects.filter(is_active=True)

    def delete(self, request, type, id):
        try:
            p = request.user.get_profile()
            p.followed_members.remove(int(id))
            return rc.DELETED
        except:
            return rc.FORBIDDEN

    def update(self, request):
        id = request.PUT.get('watch_member', None)
        if not id:
            return rc.BAD_REQUEST
        if request.user.is_authenticated():
            p = request.user.get_profile()
            try:
                p.followed_members.get(pk=id)
                return rc.DUPLICATE_ENTRY
            except Member.DoesNotExist:
                member = Member.objects.get(pk=id)
                p.followed_members.add(member)
                return member
        else:
            return rc.FORBIDDEN
