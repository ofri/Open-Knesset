#encoding: utf-8
'''
This is a django-backlinks config file to register the view on the list_detail as a pingable view
'''
from django.views.generic.list_detail import object_detail
    
from knesset.mks.models import Member
from backlinks.pingback.server import default_server
from knesset.mks.views import MemberDetailView

def get_mk_entry(slug=None):
    return Member.objects.get(pk=slug)

def mk_is_backlinkable(url, entry):
    if entry:
        return entry.backlinks_enabled
    return False
    
def mk_detail(request, slug=None, **kwargs):    
    entry = MemberDetailView(object_id=slug,
                             slug=slug,
                             request=request,
                             queryset = Member.objects.all(),
                             **kwargs)
    args = ()
    #return entry.get_context()
    return entry.GET( *args, **kwargs)

mk_detail = default_server.register_view(mk_detail, get_mk_entry, mk_is_backlinkable)

#add_view_to_registry(MemberDetailView,get_mk_entry, mk_is_backlinkable)