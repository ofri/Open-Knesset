class GetYoutubeVideos:

    GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'

    def __init__(self,q=None,max_results=20,author=None,orderby='published',videos_json=None):
        self.videos=[]
        if videos_json is None:
            params={
                'q':q, 
                'max-results':max_results, 
                'alt':'json',
                'orderby':orderby
            }
            if author is not None: params['author']=author
            url=_build_url(GDATA_YOUTUBE_VIDEOS_URL,params)
            videos_json=urllib.urlopen(url)
            yvideos=json.load(videos_json)
        else:
            yvideos=json.loads(videos_json)
        yentries=_parse_dict(yvideos,{'feed':'entry'},default=[])
        for yentry in yentries:
            video=_parse_youtube_entry(yentry)
            self.videos.append(video)

    def _parse_youtube_entry(self.yentry):
        video={
            'id':_parse_dict(yentry,{'id':'$t'}),
            'title':_parse_dict(yentry,{'title':'$t'},validate={'title':{'type':'text'}}),
            'description':_parse_dict(yentry,{'content':'$t'},validate={'content':{'type':'text'}}),
        }
        published=_parse_dict(yentry,{'published':'$t'})
        if published is not None:
            video['published']=dateutil.parser.parse(published)
        yauthors=_parse_dict(yentry,'author',default=[])
        if len(yauthors)>0:
            yauthor=yauthors[0]
            video['author']=_parse_dict(yauthor,{'name':'$t'})
        ylinks=_parse_dict(yentry,'link',[])
        for ylink in ylinks:
            link=_parse_dict(ylink,'href',validate={'type':'text/html','rel':'alternate'})
            if link is not None:
                video['link']=link
        ymediaGroup=_parse_dict(yentry,'media$group',default={})
        ymediaContents=_parse_dict(ymediaGroup,'media$content',default=[])
        for ymediaContent in ymediaContents:
            embed_url=_parse_dict(ymediaContent,'url',validate={'isDefault':'true'})
            if embed_url is not None:
                video['embed_url']=embed_url
                video['embed_url_autoplay']=embed_url+'&autoplay=1'
        ymediaThumbnails=_parse_dict(ymediaGroup,'media$thumbnail',default=[])
        if len(ymediaThumbnails)>0:
            ymediaThumbnail=ymediaThumbnails[0]
            video['thumbnail480x360']=_parse_dict(ymediaThumbnail,'url')
            if len(ymediaThumbnails)>1:
                ymediaThumbnail=ymediaThumbnails[1]
                video['thumbnail90x120']=_parse_dict(ymediaThumbnail,'url')
        return video

    

