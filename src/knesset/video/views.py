import json
from knesset.hashnav import ListView
from django.http import HttpResponse
from knesset.video.models import Video

class VideoListView (ListView):
    def GET(self, *args, **kwargs):
        #if (not self.request.user.is_authenticated()):
        #    raise Exception('You must be logged in')
        #if (not self.request.user.is_staff())
        # self.request.user
        # self.extra_context        
        self.extra_context['user']=self.request.user
        return super(VideoListView, self).GET(*args,**kwargs)

def videoListApproveAjaxView(request):
    if (request.user.is_staff):
        if request.method=='POST':
            hideVideoIds=request.POST['hideVideoIds'].split(',')
            showVideoIds=request.POST['showVideoIds'].split(',')
            updatedVideoIds=[]
            for vid in hideVideoIds:
                if len(vid)>0:
                    video=Video.objects.get(id=vid)
                    video.hide=True
                    video.reviewed=True
                    video.save()
                    updatedVideoIds.append(vid)
            for vid in showVideoIds:
                if len(vid)>0:
                    video=Video.objects.get(id=vid)
                    video.hide=False
                    video.reviewed=True
                    video.save()
                    updatedVideoIds.append(vid)
            res={
                'status':True,
                'updatedVideoIds':updatedVideoIds,
            }
        else:
            res={'status':False,'msg':'invalid request method'}
    else:
        res={'status':False,'msg':'not authenticated'}
    return HttpResponse(json.dumps(res), mimetype="application/json")