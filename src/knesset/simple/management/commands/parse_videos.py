#encoding: utf-8

import urllib, json

GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'

def get_youtube_videos(q,max_results=20,author=None):
    videos=[]
    url=GDATA_YOUTUBE_VIDEOS_URL
    # TODO: add url encoding to the query, ideally we could use utllib.quote
    # but it seems to not support unicode strings
    url+='?q='+urllib.quote(q.encode('utf-8'))
    url+='&max_results='+str(max_results)
    url+='&alt=json'
    if author is not None:
        # TODO: add url encoding
        url+='&author='+urllib.quote(author.encode('utf-8'))
    yvideos=json.load(urllib.urlopen(url))
    if 'feed' in yvideos:
        yfeed=yvideos['feed']
        if 'entry' in yfeed:
            yentries=yfeed['entry']
            for yentry in yentries:
                video={}
                if (
                    'title' in yentry
                    and 'type' in yentry['title'] and yentry['title']['type']=='text'
                    and '$t' in yentry['title']
                ):
                    video['title']=yentry['title']['$t']
                if (
                    'content' in yentry
                    and 'type' in yentry['content'] and yentry['content']['type']=='text'
                    and '$t' in yentry['content']
                ):
                    video['content']=yentry['content']['$t']
                if (
                    'author' in yentry and 'name' in yentry['author']
                    and '$t' in yentry['author']['name']
                ):
                    video['author']=yentry['author']['name']['$t']
                if 'media$group' in yentry:
                    ymediaGroup=yentry['media$group']
                    if 'media$content' in ymediaGroup:
                        ymediaContents=ymediaGroup['media$content']
                        for ymediaContent in ymediaContents:
                            if (
                                'isDefault' in ymediaContent and ymediaContent['isDefault']
                                and 'url' in ymediaContent
                            ):
                                embed_url=ymediaContent['url']
                                video['embed_url_autoplay']=embed_url+'&autoplay=1'
                    #mediaGroup['media$thumbnail'][0]['url']
                    if 'media$thumbnail' in ymediaGroup:
                        ymediaThumbnails=ymediaGroup['media$thumbnail']
                        for k in range(len(ymediaThumbnails)):
                            ymediaThumbnail=ymediaThumbnails[k]
                            if 'url' in ymediaThumbnail:
                                if k==0:
                                    video['thumbnail480x360']=ymediaThumbnail['url']
                videos.append(video)
    return videos
