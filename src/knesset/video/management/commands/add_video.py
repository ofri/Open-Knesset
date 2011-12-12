from django.core.management.base import NoArgsCommand
from optparse import make_option
import re
from knesset.video.models import Video
from knesset.video.utils.youtube import GetYoutubeVideos
from knesset.mks.models import Member

class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--video-link',action='store',dest='video-link',
            help="link to the video, use --list-types to see a list of supported link types"),
        make_option('--list-types',action='store_true',dest='list-types',
            help="list supported video link types and formats"),
        make_option('--object-type',action='store',dest='object-type',
            help="set the object type, currently only member is supported"),
        make_option('--object-id',action='store',dest='object-id',
            help="set the object id that the video will be related to"),
        make_option('--sticky',action='store_true',dest='is_sticky',
            help="set the video as sticky"),
    )
    help = "add a video"    

    def _getVideoDataFromUrl(self,url):
        matches=[
            ('youtube',re.search('v=([0-9a-zA-Z_]*)$',url)),
            ('youtube',re.search('v=([0-9a-zA-Z_]*)&',url)),
        ]
        ans=None
        for line in matches:
            source_type=line[0]
            match=line[1]
            if match is not None and len(match.groups())>0:
                if source_type=='youtube':
                    source_id=match.groups()[0]
                    source_id='http://gdata.youtube.com/feeds/api/videos/'+source_id
                    ans={
                        'source_type':source_type,
                        'source_id':source_id,
                    }
        return ans
    
    def _saveYoutubeVideoFromSource(self,v,obj):
        if len(v['source_id'])>0:
            videos=GetYoutubeVideos(youtube_id_url=v['source_id']).videos
            if len(videos)==1:
                video=videos[0]
                if type(obj).__name__=='Member':
                    return update_member_related_video(obj,video)
    
    def _saveVideoFromSource(self,v,obj):
        if v['source_type']=='youtube':
            return self._saveYoutubeVideoFromSource(v,obj)

    def handle_noargs(self, **options):
        video_link=options.get('video-link',None)
        list_types=options.get('list-types',False)
        object_type=options.get('object-type',None)
        object_id=options.get('object-id',None)
        is_sticky=options.get('is_sticky',False)
        
        if list_types:
            print """Supported link formats:
youtube - 
http://www.youtube.com/xxx/ddd"""
        elif video_link is None or object_type is None or object_id is None:
            print "you must specify a video link, object type and object id, run with -h for help"
        else:
            obj=None
            if object_type=='member':
                obj=Member.objects.get(id=object_id)
            else:
                print 'unsupported object type.'
            if obj is not None:
                v=None
                video=self._getVideoDataFromUrl(video_link)
                if video is not None:
                    v=self._saveVideoFromSource(video,obj)                    
                if type(v).__name__=='Video' and v.id is not None:
                    if is_sticky:
                        v.sticky=True
                        v.save()
                    print "video was added successfuly"
                    print "id: "+str(v.id)
                else:
                    print "failed to add the video, check if the video alreayd exists:"
                    print "$bin/django shell_plus"
                    print ">>> Video.objects.filter(source_id='"+video['source_id']+"')"
                

