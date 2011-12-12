import urllib, json, dateutil.parser
from knesset.video.utils import build_url
from knesset.video.utils.parse_dict import parse_dict

class GetYoutubeVideos:

    GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'

    def __init__(
        self,q=None,max_results=20,author=None,orderby='published',
        videos_json=None,youtube_id_url=None,
        limit_time='all_time'
    ):
        """
            perform search on youtube
            parameters:
            q: (string) the query to search for
            max_results: (int) maximum number of results to return
            author: (string) limit to videos uploaded by this youtube user
            orderby: (string) how to order the videos, possible values:
                        relevance, published, viewCount, rating
            limit_time: (string) limit to videos uploaded in a certain timeframe
                        possible values: today, this_week, this_month, all_time
        """
        self.videos=[]
        if videos_json is None and youtube_id_url is not None:
            videos_json=urllib.urlopen(youtube_id_url+'?alt=json').read()
        if videos_json is None and q is not None:
            params={
                'q':q, 
                'max-results':max_results, 
                'alt':'json',
                'orderby':orderby
            }
            if author is not None: params['author']=author
            if limit_time is not None: params['time']=limit_time
            url=build_url(self.GDATA_YOUTUBE_VIDEOS_URL,params)
            videos_json=urllib.urlopen(url).read()
        if videos_json is not None and len(videos_json)>0:
            yvideos=json.loads(videos_json)
            yentries=parse_dict(yvideos,{'feed':'entry'})
            if yentries is None:
                yentry=parse_dict(yvideos,'entry')
                if yentry is None:
                    yentries=[]
                else:
                    yentries=[yentry]
            for yentry in yentries:
                video=self._parse_youtube_entry(yentry)
                self.videos.append(video)

    def _parse_youtube_entry(self,yentry):
        video={
            'id':parse_dict(yentry,{'id':'$t'}),
            'title':parse_dict(yentry,{'title':'$t'},validate={'title':{'type':'text'}}),
            'description':parse_dict(yentry,{'content':'$t'},validate={'content':{'type':'text'}}),
        }
        published=parse_dict(yentry,{'published':'$t'})
        if published is not None:
            video['published']=dateutil.parser.parse(published)
        yauthors=parse_dict(yentry,'author',default=[])
        if len(yauthors)>0:
            yauthor=yauthors[0]
            video['author']=parse_dict(yauthor,{'name':'$t'})
        ylinks=parse_dict(yentry,'link',default=[])
        for ylink in ylinks:
            link=parse_dict(ylink,'href',validate={'type':'text/html','rel':'alternate'})
            if link is not None:
                video['link']=link
        ymediaGroup=parse_dict(yentry,'media$group',default={})
        ymediaContents=parse_dict(ymediaGroup,'media$content',default=[])
        for ymediaContent in ymediaContents:
            embed_url=parse_dict(ymediaContent,'url',validate={'isDefault':'true'})
            if embed_url is not None:
                video['embed_url']=embed_url
                video['embed_url_autoplay']=embed_url+'&autoplay=1'
        ymediaThumbnails=parse_dict(ymediaGroup,'media$thumbnail',default=[])
        if len(ymediaThumbnails)>0:
            ymediaThumbnail=ymediaThumbnails[0]
            video['thumbnail480x360']=parse_dict(ymediaThumbnail,'url')
            if len(ymediaThumbnails)>1:
                ymediaThumbnail=ymediaThumbnails[1]
                video['thumbnail90x120']=parse_dict(ymediaThumbnail,'url')
        return video
