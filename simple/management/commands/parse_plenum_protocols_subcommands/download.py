# encoding: utf-8

import urllib,urllib2,re,datetime,traceback,sys,os
from BeautifulSoup import BeautifulSoup
from django.conf import settings

URL="http://www.knesset.gov.il/plenum/heb/plenum_queue.aspx"
ROBOTS_URL="http://www.knesset.gov.il/robots.txt"
FULL_URL="http://www.knesset.gov.il/plenum/heb/display_full.asp"
FILE_BASE_URL="http://www.knesset.gov.il/plenum/heb/"
WORDS_OF_THE_KNESSET=u"דברי הכנסת"
WORDS_OF_THE_KNESSET_FULL=u"כל הפרוטוקול"
DISCUSSIONS_ON_DATE=u"הדיונים בתאריך"

verbosity=1

def _debug(str):
    global verbosity
    if verbosity>1: print str

def _get_committees_index_page(full):
    if full:
        url=FULL_URL
        encoding='iso_8859_8'
    else:
        url=URL
        encoding='utf8'
    _debug('getting the html from '+url)
    try:
        return unicode(urllib2.urlopen(url).read(),encoding)
    except Exception, e:
        print 'could not fetch committees_index_page, exception: '+str(e)
        traceback.print_exc(file=sys.stdout)

def _copy(url,to):
    _debug("copying from "+url+" to "+to)
    d=os.path.dirname(to)
    if not os.path.exists(d):
        os.makedirs(d)
    if not os.path.exists(to):
        urllib.urlretrieve(url,to+".tmp")
        os.rename(to+'.tmp',to)
    else:
        _debug('already downloaded')

#def _downloadRobots():
    #f=urllib2.urlopen(ROBOTS_URL)
    #for line in f:
        #res=re.search(r"^Disallow: (.*)$",line)
        #if res is not None:
            #path=res.group(1)

def _downloadLatest(full):
    html=_get_committees_index_page(full)
    soup=BeautifulSoup(html)
    if full:
        words_of_the_knesset=WORDS_OF_THE_KNESSET_FULL
    else:
        words_of_the_knesset=WORDS_OF_THE_KNESSET
    aelts=soup('a',text=words_of_the_knesset)
    for aelt in aelts:
        selt=aelt.findPrevious('span',text=re.compile(DISCUSSIONS_ON_DATE))
        url=FILE_BASE_URL+aelt.parent.get('href')
        filename=re.search(r"[^/]*$",url).group()
        _debug(filename)
        m=re.search(r"\((.*)/(.*)/(.*)\)",selt)
        if m is None:
            selt=selt.findNext()
            m=re.search(r"\((.*)/(.*)/(.*)\)",unicode(selt))
        if m is not None:
            day=m.group(1)
            mon=m.group(2)
            year=m.group(3)
            DATA_ROOT = getattr(settings, 'DATA_ROOT')
            _copy(url.replace('/heb/..',''),DATA_ROOT+'plenum_protocols/'+year+'/'+mon+'/'+day+'/'+filename)

def Download(verbosity_level,robots):
    global verbosity
    verbosity=int(verbosity_level)
    if (robots):
        #_downloadRobots()
        print "not implemented yet"
    else:
        _downloadLatest(False)
        _downloadLatest(True)

