# encoding: utf-8

from knesset.video.management.commands.sub_commands import SubCommand
from knesset.committees.models import Committee
from BeautifulSoup import BeautifulSoup
import urllib,re,datetime
from knesset.video.utils import get_videos_queryset
from knesset.video.models import Video

class UpdateCommitteesVideos(SubCommand):

    PORTAL_KNESSET_COMMITTEES_INDEX_PAGE_URL='http://www.knesset.gov.il/committees/heb/current_vaadot.asp'
    
    PORTAL_KNESSET_BASEHREF='http://portal.knesset.gov.il'
    
    KNESSET_BASEHREF='http://www.knesset.gov.il'

    def __init__(self,command,committees=None):
        SubCommand.__init__(self,command)
        if self._get_opt('with-history'):
            self._error('download of historical data is not supported yet')
        if committees is None: committees=Committee.objects.all()
        for comm in committees:
            self._debug(comm.name)
            self._check_timer()
            broadcasts_url=comm.portal_knesset_broadcasts_url
            if len(broadcasts_url)==0:
                broadcasts_url=self._update_committee_broadcasts_url(comm)
            if len(broadcasts_url)>0:
                videos=self._get_committee_videos(broadcasts_url)
                for video in videos:
                    self._update_committee_mms_video(comm,video)
            else:
                self._warn('no broadcasts url :'+comm.name)

    def _get_committees_index_page(self):
        rf=urllib.urlopen(self.PORTAL_KNESSET_COMMITTEES_INDEX_PAGE_URL)
        return rf.read().decode('windows-1255').encode('utf-8')
        
    def _get_committee_mainpage(self,soup,name):
        self._debug('_get_committee_mainpage')
        href=''
        portal_havaada=u'פורטל הוועדה'
        elt=soup('b',text=name)
        if len(elt)>0:
            elt=elt[0].findAllNext('a',text=portal_havaada)
            if len(elt)>0:
                elt=elt[0]
                href=elt.parent['href']
        if len(href)>6:
            if href[0]=='/':
                href=self.KNESSET_BASEHREF+href
            self._debug(href)
            try:
                return self._get_committee_mainpage_soup(href)
            except Exception:
                self._error('exception in get_committee_mainpage_soup, href='+href)
                return ''
        else:
            return ''
        
    def _get_committee_mainpage_soup(self,href):
        return BeautifulSoup(urllib.urlopen(href).read())
              
    def _update_committee_broadcasts_url(self,comm):
        self._debug('_update_committee_broadcasts_url')
        url=''
        index=self._get_committees_index_page()
        soup=BeautifulSoup(index)
        main=self._get_committee_mainpage(soup,comm.name)
        if type(main).__name__=='BeautifulSoup':
            vaadot_meshudarot=u'ועדות משודרות'
            elt=main('a',text=vaadot_meshudarot)
            if len(elt)>0:
                path=elt[0].parent['href']
                url=self.PORTAL_KNESSET_BASEHREF+path
        if len(url)>6:
            self._debug(url)
            self._update_committee_portal_knesset_broadcasts_url(comm,url)
        return url
    
    def _update_committee_portal_knesset_broadcasts_url(self,comm,url):
        comm.portal_knesset_broadcasts_url=url
        comm.save()
    
    def _get_committee_videos_soup(self,bcasturl):
        return BeautifulSoup(urllib.urlopen(bcasturl).read())
    
    def _get_committee_videos(self,bcasturl):
        self._debug('_get_committee_videos')
        videos=[]
        mmsurls=[]
        try:
            soup=self._get_committee_videos_soup(bcasturl)
        except Exception:
            self._error('exception in _get_committee_videos_soup, bcasturl='+bcasturl)
            return videos
        elts=soup('span',{'onclick':re.compile(".*asf.*")})
        if len(elts)>0:
            for elt in elts:
                onclick=elt['onclick']
                r=re.compile("SetPlayerFileName\\('(.*),([0-9]*)/([0-9]*)/([0-9]*) ([0-9]*):([0-9]*):([0-9]*) (.*)'\\);")
                mtch=re.search(r,onclick)
                groups=mtch.groups()
                if len(groups)==8:
                    mmsurl=groups[0]
                    if mmsurl not in mmsurls:
                        title=groups[7]
                        # try to get a better title
                        while elt.nextSibling is not None:
                            elt=elt.nextSibling
                            if len(elt.string)>len(title):
                                title=elt.string
                                break
                        title=re.sub('^[0-9]*\. ', '', title)
                        title=re.sub("\n", '', title)
                        title=re.sub("``", "'", title)
                        title=title.strip()
                        self._debug(mmsurl)
                        mmsurls.append(mmsurl)
                        videos.append({
                            'mmsurl':mmsurl,
                            'title':title,
                            'datetime':datetime.datetime(int(groups[3]),int(groups[2]),int(groups[1]),int(groups[4]),int(groups[5]),int(groups[6])),
                        })
        return videos
    
    def _get_committee_num_mms_videos(self,comm,group,ignoreHide,embed_link):
        return get_videos_queryset(comm,group=group,ignoreHide=ignoreHide).filter(embed_link=embed_link).count()
    
    def _getMmsVideoFields(self,video,comm):
        return {
            'embed_link':video['mmsurl'],
            'title':video['title'],
            'source_type':'mms-knesset-portal',
            'published':video['datetime'],
            'group':'mms',
            'content_object':comm
        }
        
    def _saveVideo(self,videoFields):
        v=Video(**videoFields)
        v.save()
    
    def _update_committee_mms_video(self,comm,video):
        self._debug('_update_committee_mms_video')
        numcurvids=self._get_committee_num_mms_videos(comm, 'mms', True, video['mmsurl'])
        if numcurvids==0:
            self._saveVideo(self._getMmsVideoFields(video, comm))
