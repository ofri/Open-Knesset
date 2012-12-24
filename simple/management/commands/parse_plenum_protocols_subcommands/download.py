# encoding: utf-8

import urllib,urllib2,re,datetime,traceback,sys,os
from BeautifulSoup import BeautifulSoup
from django.conf import settings

URL="http://www.knesset.gov.il/plenum/heb/plenum_queue.aspx"
FILE_BASE_URL="http://www.knesset.gov.il/plenum/heb/"
WORDS_OF_THE_KNESSET=u"דברי הכנסת"
DISCUSSIONS_ON_DATE=u"הדיונים בתאריך"

def _debug(str):
    print str

def _get_committees_index_page():
    _debug('getting the html from '+URL)
    try:
        return unicode(urllib2.urlopen(URL).read(),'utf8')
    except Exception, e:
        print 'could not fetch committees_index_page, exception: '+str(e)
        traceback.print_exc(file=sys.stdout)

def _copy(url,to):
    _debug("copying from "+url+" to "+to)
    d=os.path.dirname(to)
    if not os.path.exists(d):
        os.makedirs(d)
    urllib.urlretrieve(url,to)

def Download():
    soup=BeautifulSoup(_get_committees_index_page())
    aelts=soup('a',text=WORDS_OF_THE_KNESSET)
    for aelt in aelts:
        selt=aelt.findPrevious('span',text=re.compile(DISCUSSIONS_ON_DATE))
        url=FILE_BASE_URL+aelt.parent.get('href')
        filename=re.search(r"[^/]*$",url).group()
        m=re.search(r"\((.*)/(.*)/(.*)\)",selt)
        day=m.group(1)
        mon=m.group(2)
        year=m.group(3)
        DATA_ROOT = getattr(settings, 'DATA_ROOT')
        _copy(url,DATA_ROOT+'plenum_protocols/'+year+'/'+mon+'/'+day+'/'+filename)

