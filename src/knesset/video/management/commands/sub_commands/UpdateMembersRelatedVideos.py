# encoding: utf-8

from knesset.video.management.commands.sub_commands import SubCommand
from knesset.video.utils.youtube import GetYoutubeVideos
from knesset.mks.models import Member
from knesset.video.utils.parse_dict import validate_dict
from knesset.video.utils import get_videos_queryset
from knesset.video.models import Video

class UpdateMembersRelatedVideos(SubCommand):
    
    def __init__(self,command,members=None):
        SubCommand.__init__(self,command)
        if members is None: members=Member.objects.all()
        for member in members:
            self._debug(member.name)
            self._check_timer()
            relvids=[]
            for name in member.names:
                self._debug(name)
                for video in self._getVideosForMember(name):
                    if self._verify_related_video(video,name):
                        relvids.append(video)
            if len(relvids)>0:
                for video in relvids:
                    self._update_member_related_video(member,video)
                
    def _getVideosForMember(self,name):
        return GetYoutubeVideos(q='"'+name+'"',max_results=15,limit_time='this_month').videos

    def _verify_related_video(self,video,name):
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

    def _getVideoFields(self,video,member):
        return {
            'embed_link':video['embed_url_autoplay'],
            'small_image_link':video['thumbnail90x120'],
            'title':video['title'],
            'description':video['description'],
            'link':video['link'],
            'source_type':'youtube', 
            'source_id':video['id'],
            'published':video['published'],
            'group':'related', 
            'content_object':member
        }
        
    def _isMemberHaveVideo(self,member,video):
        qs=get_videos_queryset(member,ignoreHide=True)
        qs=qs.filter(source_id=video['id'],source_type='youtube')
        return qs.count()>0

    def _saveVideo(self,videoFields):
        v=Video(**videoFields)
        v.save()

    def _update_member_related_video(self,member,video):
        if not self._isMemberHaveVideo(member, video):
            self._saveVideo(self._getVideoFields(video, member))
