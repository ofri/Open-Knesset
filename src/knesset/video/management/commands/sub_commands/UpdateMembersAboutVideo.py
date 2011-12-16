# encoding: utf-8
from knesset.mks.models import Member
from knesset.video.utils import get_videos_queryset
from knesset.video.utils.youtube import GetYoutubeVideos
from knesset.video.management.commands.sub_commands import SubCommand
from knesset.video.utils.parse_dict import validate_dict
from knesset.video.models import Video

class UpdateMembersAboutVideo(SubCommand):

    def __init__(self,command,members=None):
        SubCommand.__init__(self,command)
        if members is None: members=Member.objects.all()
        for member in members:
            self._debug(member.name)
            self._check_timer()
            if not self._isMemberHaveAboutVideo(member):
                names=member.names
                got_video=False
                for name in names:
                    videos=self._getVideosForMemberName(name)
                    for video in videos:
                        if self._update_member_about_video(member,video,names):
                            got_video=True
                            break
                    if got_video:
                        break

    def _getVideosForMemberName(self,name):
        return GetYoutubeVideos(q=u"כרטיס ביקור ערוץ הכנסת "+name).videos

    def _isMemberHaveAboutVideo(self,member):
        qs=get_videos_queryset(member, group='about', ignoreHide=True)
        return qs.count()>0

    def _getVideoFields(self,result_video,member):
        return {
            'embed_link':result_video['embed_url_autoplay'],
            'image_link':result_video['thumbnail480x360'],
            'title':result_video['title'],
            'description':result_video['description'],
            'link':result_video['link'],
            'source_type':'youtube', 
            'source_id':result_video['id'],
            'published':result_video['published'],
            'group':'about', 
            'content_object':member
        }

    def _saveVideo(self,videoFields):
        v=Video(**videoFields)
        v.save()

    def _update_member_about_video(self,member,video,names):
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
            self._saveVideo(self._getVideoFields(result_video, member))
            return True

