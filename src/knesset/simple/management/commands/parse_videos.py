#encoding: utf-8

import urllib, json

GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'

def get_youtube_videos(queries,max_results):
    for q in queries:
        url=GDATA_YOUTUBE_VIDEOS_URL
        # TODO: add url encoding to the query, ideally we could use utllib.quote
        # but it seems to not support unicode strings
        url+='?q='+q
        url+='&max_results='+str(max_results)
        url+='&alt=json'
        print url

"""
class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        print "get youtube videos"
        url="https://gdata.youtube.com/feeds/api/videos"
        url+='?q=ערוץ+הכנסת+כרטיס+ביקור+ח"כ+דב+חנין'
        url+="&max-results=1"
        url+="&alt=json"
        print url
        feed=json.load(urllib.urlopen(url))
        entries=feed['feed']['entry']
        if len(entries)==1:
            mediaGroup=entries[0]['media$group']
            mediaContents=mediaGroup['media$content']
            for mediaContent in mediaContents:
                if 'isDefault' in mediaContent and mediaContent['isDefault']:
                    embed_link=mediaContent['url']+'&autoplay=1'
            image_link=mediaGroup['media$thumbnail'][0]['url']
        if 'image_link' in locals() and 'embed_link' in locals():
            print image_link
            print embed_link
"""
