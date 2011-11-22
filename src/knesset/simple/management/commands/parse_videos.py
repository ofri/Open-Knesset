#encoding: utf-8

import urllib, json

GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'

def get_youtube_videos(q,max_results=20,author=None):
    videos=[]
    url=GDATA_YOUTUBE_VIDEOS_URL
    url+='?q='+urllib.quote(q.encode('utf-8'))
    url+='&max_results='+str(max_results)
    url+='&alt=json'
    if author is not None:
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
                    if 'media$thumbnail' in ymediaGroup:
                        ymediaThumbnails=ymediaGroup['media$thumbnail']
                        for k in range(len(ymediaThumbnails)):
                            ymediaThumbnail=ymediaThumbnails[k]
                            if 'url' in ymediaThumbnail:
                                if k==0:
                                    video['thumbnail480x360']=ymediaThumbnail['url']
                videos.append(video)
    return videos
    

def update_mk_about_video(self):
    for member in Member.objects.all():
        if member.about_video_embed_link is None:
            videos=get_youtube_videos(q=u"כרטיס ביקור ערוץ הכנסת "+member.name)
            result_video=None
            for video in videos:
                if (
                    'title' in video
                    and 'embed_url_autoplay' in video
                    and 'thumbnail480x360' in video
                ):
                    title=video['title']
                    if (
                        u'כרטיס ביקור' in title
                        and u'ערוץ הכנסת' in title
                    ):
                        if member.name in title:
                            result_video=video
                        else:
                            for altname in member.memberaltname_set.all():
                                if altname in title:
                                    result_video=video
                                    break
                        if result_video is not None:
                            break
            if result_video is not None:
                member.about_video_embed_link=video['embed_url_autoplay']
                member.about_video_image_link=video['thumbnail480x360']
                member.save()

