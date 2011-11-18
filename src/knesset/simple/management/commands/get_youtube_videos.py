#encoding: utf-8

import urllib, json
from django.core.management.base import NoArgsCommand


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

def test():
    print "hello"
    
#############
#   Main    #
#############
if __name__ == '__main__':
    test()

