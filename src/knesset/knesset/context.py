from django.conf import settings

d = {'debug':getattr(settings,'LOCAL_DEV',False)}

def processor(request):
    return d
