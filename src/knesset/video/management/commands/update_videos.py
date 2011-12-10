# encoding: utf-8

from knesset.mks.models import Member
from knesset.video.models import Video
from knesset.video.utils import get_videos_queryset,update_member_related_video
from knesset.video.utils.parse_dict import validate_dict
from knesset.video.utils.youtube import get_youtube_videos
from django.core.management.base import NoArgsCommand

#### member - about video ####

def _update_member_about_video(member,video,names):
    result_video=None
    if validate_dict(video,[
        'title','embed_url_autoplay','thumbnail480x360',
        'id','description','link','published'
    ]):
        title=video['title']
        if (
            u'כרטיס ביקור' in title
            and u'ערוץ הכנסת' in title
        ):
            for name in names:
                if name in title:
                    result_video=video
                    break
    if result_video is None:
        return False
    else:
        v = Video(
            embed_link=result_video['embed_url_autoplay'],
            image_link=result_video['thumbnail480x360'],
            title=result_video['title'],
            description=result_video['description'],
            link=result_video['link'],
            source_type='youtube', 
            source_id=result_video['id'],
            published=result_video['published'],
            group='about', 
            content_object=member
        )
        v.save()
        return True

def update_members_about_video():
    for member in Member.objects.all():
        if get_videos_queryset(member,group='about').count()==0:
            names=_get_member_names(member)
            got_video=False
            for name in names:
                videos=get_youtube_videos(q=u"כרטיס ביקור ערוץ הכנסת "+name)
                for video in videos:
                    if _update_member_about_video(member,video,names):
                        got_video=True
                        break
                if got_video:
                    break

#### member - related videos ####

def _verify_related_video(video,name):
    if validate_dict(video,['title','description']):
        titledesc=video['title']+video['description']
        if (
            validate_dict(video,['embed_url_autoplay','thumbnail90x120','id','link','published'])
            and name in titledesc
            and video['published'] is not None
        ):
            return True
        else:
            return False
    else:
        return False

def update_members_related_videos():
    for member in Member.objects.all():
        relvids=[]
        names=_get_member_names(member)
        for name in names:
            namerelvids=[]
            videos=get_youtube_videos(q='"'+name+'"',max_results=15)
            for video in videos:
                if _verify_related_video(video,name):
                    namerelvids.append(video)
                if len(namerelvids)==5:
                    break
            if len(namerelvids)>0:
                relvids=relvids+namerelvids
        if len(relvids)>0:
            for video in relvids:
                update_member_related_video(member,video)

#### Command ####

class Command(NoArgsCommand):

        def handle_noargs(self, **options):
            update_members_about_video()
            update_members_related_videos()

