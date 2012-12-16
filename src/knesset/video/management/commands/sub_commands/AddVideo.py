# encoding: utf-8

import re
from mks.models import Member
from video.utils.youtube import GetYoutubeVideos
from video.utils import get_videos_queryset
from video.models import Video
from video.utils.parse_dict import validate_dict

class AddVideo():

    def __init__(self,options):
        self._video_link=options.get('video-link', None)
        self._object_type=options.get('object-type', None)
        self._object_id=options.get('object-id', None)
        self._sticky=options.get('is_sticky', False)

    def run(self):
        ret=False
        if (
            self._video_link is None
            or self._object_type is None
            or self._object_id is None
        ):

            self.ans="you must specify a video link, object type and object id, run with -h for help"
        else:
            video={}
            if self._object_type=='member':
                video['content_object']=self._getMemberObject(id=self._object_id)
                video['group']='related'
            else:
                self.ans='unsupported object type, run with -h for help'
            if 'content_object' in video:
                video=self._getVideoDataFromUrl(self._video_link,video)
                if 'source_type' in video:
                    video=self._saveVideoFromSource(video)
                    if video is not None and video.id is not None:
                        if self._sticky:
                            video.sticky=True
                            video.save()
                        self.ans="video was added successfuly, id: "+str(video.id)
                        ret=True
                    else:
                        self.ans="failed to add the video"
                else:
                    self.ans='unable to determine source type from url'
        return ret

    def _saveYoutubeVideoFromSource(self,video):
        if len(video['source_id'])>0:
            yvideos=self._getYoutubeVideos(youtube_id_url=video['source_id'])
            if len(yvideos)>0:
                yvideo=yvideos[0]
                if not self._isVideoExists(video) and self._validateYoutubeVideo(yvideo):
                    return self._saveVideo(self._getYoutubeVideoFields(yvideo,video))
        return None

    def _validateYoutubeVideo(self,video):
        return validate_dict(video,[
            'embed_url_autoplay',
            'thumbnail480x360',
            'thumbnail90x120',
            'title',
            'description',
            'link',
            'id',
            'published',
        ])

    def _getYoutubeVideoFields(self,yvideo,video):
        return {
            'embed_link':yvideo['embed_url_autoplay'],
            'image_link':yvideo['thumbnail480x360'],
            'small_image_link':yvideo['thumbnail90x120'],
            'title':yvideo['title'],
            'description':yvideo['description'],
            'link':yvideo['link'],
            'source_type':'youtube',
            'source_id':yvideo['id'],
            'published':yvideo['published'],
            'group':video['group'],
            'content_object':video['content_object']
        }

    def _saveVideoFromSource(self,video):
        if video['source_type']=='youtube':
            return self._saveYoutubeVideoFromSource(video)
        else:
            raise Exception('unknown source type')

    def _getVideoDataFromUrl(self,url,video):
        matches=[
            ('youtube',re.search('v=([0-9a-zA-Z_]*)$',url)),
            ('youtube',re.search('v=([0-9a-zA-Z_]*)&',url)),
        ]
        for line in matches:
            source_type=line[0]
            match=line[1]
            if match is not None and len(match.groups())>0:
                if source_type=='youtube':
                    source_id=match.groups()[0]
                    source_id='http://gdata.youtube.com/feeds/api/videos/'+source_id
                    video['source_type']=source_type
                    video['source_id']=source_id
        return video



    # low level functions for overide in testing

    def _getMemberObject(self,**kwargs):
        return Member.objects.get(**kwargs)

    def _getYoutubeVideos(self,**kwargs):
        return GetYoutubeVideos(**kwargs).videos

    def _isVideoExists(self,video):
        return get_videos_queryset(video['content_object'],ignoreHide=True).filter(source_id=video['source_id']).count()>0

    def _saveVideo(self,videoFields):
        video=Video(**videoFields)
        video.save()
        return video
