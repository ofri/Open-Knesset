# encoding: utf-8
from knesset.mks.models import Member
from knesset.video.utils import get_videos_queryset
from knesset.video.utils.youtube import get_youtube_videos

class UpdateMembersAboutVideo:

    def __init__(self):
        for member in Member.objects.all():
        if get_videos_queryset(member,group='about').count()==0:
            names=member.all_names
            got_video=False
            for name in names:
                videos=get_youtube_videos(q=u"כרטיס ביקור ערוץ הכנסת "+name)
                for video in videos:
                    if _update_member_about_video(member,video,names):
                        got_video=True
                        break
                if got_video:
                    break

    def _update_member_about_video(member,video,names):
        result_video=None
        if _validate_dict(video,[
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

