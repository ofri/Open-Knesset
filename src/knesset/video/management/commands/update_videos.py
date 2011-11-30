# encoding: utf-8
import urllib, json, logging, os, re, datetime
from knesset.mks.models import Member
from knesset.video.models import Video
from django.contrib.contenttypes.models import ContentType
from knesset.video.utils import get_videos_queryset
from django.core.management.base import NoArgsCommand
import dateutil.parser
from optparse import make_option
from knesset.committees.models import Committee
from django.conf import settings
from BeautifulSoup import BeautifulSoup

GDATA_YOUTUBE_VIDEOS_URL='https://gdata.youtube.com/feeds/api/videos'
PORTAL_KNESSET_COMMITTEES_INDEX_PAGE_URL='http://www.knesset.gov.il/committees/heb/current_vaadot.asp'
PORTAL_KNESSET_BASEHREF='http://portal.knesset.gov.il'

DATA_ROOT = getattr(settings, 'DATA_ROOT',
                    os.path.join(settings.PROJECT_ROOT, os.path.pardir, os.path.pardir, 'data'))

logger = logging.getLogger("open-knesset.updatevideos")

#### misc ####

def _validate_dict(h,*args):
    for arg in args:
        if type(h).__name__=='dict' and type(arg).__name__=='list':
            for key in arg:
                if key not in h:
                    return False
        elif type(h).__name__=='dict' and type(arg).__name__=='dict':
            for k in arg:
                if k not in h:
                    return False
                v=arg[k]
                val=h[k]
                ans=_validate_dict(val,v)
                if ans==False:
                    return False
        elif type(arg).__name__=='str':
            if arg!=h:
                return False
        else:
            return False
    return True
    
def _parse_dict(h,p,validate=None,default=None):
    if type(h).__name__!='dict':
        return default
    if validate is not None and _validate_dict(h,validate)==False:
        return default
    if type(p).__name__=='str':
        if p in h:
            return h[p]
        else:
            return default
    elif type(p).__name__=='dict':
        for k in p:
            if k not in h:
                return default
            else:
                val=h[k]
                v=p[k]
                return _parse_dict(val,v,default=default)
            
    else:
        return default
    
def _build_url(url,q):
    params=[]
    for k in q:
        v=q[k]
        if v is None:
            v=''
        elif type(v).__name__!='unicode':
            v=str(v)
        v=urllib.quote(v.encode('utf-8'))
        k=urllib.quote(str(k).encode('utf-8'))
        params.append(k+'='+v)
    return url+'?'+"&".join(params)

#### youtube ####

def _parse_youtube_entry(yentry):
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

def get_youtube_videos(q=None,max_results=20,author=None,orderby='published',videos_json=None):
    videos=[]
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
        videos.append(video)
    return videos
    
#### member - misc functions ####

def _get_member_names(member):
    names=[member.name]
    for altname in member.memberaltname_set.all():
        names.append(altname)
    return names

#### member - about video ####

def _update_member_about_video(member,video,names):
    result_video=None
    if _validate_dict(video,[
        'title','embed_url_autoplay','thumbnail480x360',
        'id','description','link','published'
    ]):
        title=video['title']
        if (
            u'כרטיס ביקור' in title
            and u'ערוץ הכנסת' in title
        ):
            for name in names:
                if name in title:
                    result_video=video
                    break
    if result_video is None:
        return False
    else:
        v = Video(
            embed_link=result_video['embed_url_autoplay'],
            image_link=result_video['thumbnail480x360'],
            title=result_video['title'],
            description=result_video['description'],
            link=result_video['link'],
            source_type='youtube', 
            source_id=result_video['id'],
            published=result_video['published'],
            group='about', 
            content_object=member
        )
        v.save()
        return True

def update_members_about_video():
    logger.info('begin update_members_about_video')
    for member in Member.objects.all():
        if get_videos_queryset(member,group='about').count()==0:
            names=_get_member_names(member)
            got_video=False
            for name in names:
                videos=get_youtube_videos(q=u"כרטיס ביקור ערוץ הכנסת "+name)
                for video in videos:
                    if _update_member_about_video(member,video,names):
                        got_video=True
                        break
                if got_video:
                    break

#### member - related videos ####

def _verify_related_video(video,name):
    if _validate_dict(video,['title','description']):
        titledesc=video['title']+video['description']
        if (
            _validate_dict(video,['embed_url_autoplay','thumbnail90x120','id','link','published'])
            and name in titledesc
            and video['published'] is not None
        ):
            return True
        else:
            return False
    else:
        return False

def _update_member_related_video(member,video):
    cnt=get_videos_queryset(member).filter(source_id=video['id'],source_type='youtube').count()
    if cnt==0:
        v = Video(
            embed_link=video['embed_url_autoplay'],
            small_image_link=video['thumbnail90x120'],
            title=video['title'],
            description=video['description'],
            link=video['link'],
            source_type='youtube', 
            source_id=video['id'],
            published=video['published'],
            group='related', 
            content_object=member
        )
        v.save()
        return True
    else:
        return False

def update_members_related_videos():
    logger.info('begin update_members_related_videos')
    for member in Member.objects.all():
        relvids=[]
        names=_get_member_names(member)
        for name in names:
            namerelvids=[]
            videos=get_youtube_videos(q='"'+name+'"',max_results=15)
            for video in videos:
                if _verify_related_video(video,name):
                    namerelvids.append(video)
                if len(namerelvids)==5:
                    break
            if len(namerelvids)>0:
                relvids=relvids+namerelvids
        if len(relvids)>0:
            for video in relvids:
                _update_member_related_video(member,video)

#### committees ####

def _get_committees_index_page():
    rf=urllib.urlopen(PORTAL_KNESSET_COMMITTEES_INDEX_PAGE_URL)
    return rf.read().decode('windows-1255').encode('utf-8')
    
def _get_committee_mainpage(soup,name):
    href=''
    portal_havaada=u'פורטל הוועדה'
    elt=soup('b',text=name)
    if len(elt)>0:
        elt=elt[0].findAllNext('a',text=portal_havaada)
        if len(elt)>0:
            elt=elt[0]
            href=elt.parent['href']
    if len(href)>6:
        return BeautifulSoup(urllib.urlopen(href).read())
    else:
        return ''

def _update_committee_broadcasts_url(comm):
    url=''
    index=_get_committees_index_page()
    soup=BeautifulSoup(index)
    main=_get_committee_mainpage(soup,comm.name)
    if type(main).__name__=='BeautifulSoup':
        vaadot_meshudarot=u'ועדות משודרות'
        elt=main('a',text=vaadot_meshudarot)
        if len(elt)>0:
            path=elt[0].parent['href']
            url=PORTAL_KNESSET_BASEHREF+path
    if len(url)>6:
        comm.portal_knesset_broadcasts_url=url
        comm.save()
    else:
        print comm.name+": no broadcasts_url!"
    return url

def _get_committee_videos(bcasturl):
    videos=[]
    soup=BeautifulSoup(urllib.urlopen(bcasturl).read())
    elts=soup('span',{'onclick':re.compile(".*asf.*")})
    if len(elts)>0:
        for elt in elts:
            onclick=elt['onclick']
            r=re.compile("SetPlayerFileName\\('(.*),([0-9]*)/([0-9]*)/([0-9]*) ([0-9]*):([0-9]*):([0-9]*) (.*)'\\);")
            mtch=re.search(r,onclick)
            groups=mtch.groups()
            if len(groups)==8:
                videos.append({
                    'mmsurl':groups[0],
                    'title':groups[7],
                    'datetime':datetime.datetime(int(groups[3]),int(groups[2]),int(groups[1]),int(groups[4]),int(groups[5]),int(groups[6])),
                })
    return videos

def _update_committee_mms_video(comm,video):
    curvids=get_videos_queryset(comm,'mms').filter(embed_link=video['mmsurl'])
    if len(curvids)==0:
        v = Video(
            embed_link=video['mmsurl'],
            title=video['title'],
            source_type='mms-knesset-portal',
            published=video['datetime'],
            group='mms', 
            content_object=comm
        )
        v.save()

def download_committees_metadata(with_history):
    if with_history:
        raise Exception('download of historical data is not supported yet')
    for comm in Committee.objects.all():
        broadcasts_url=comm.portal_knesset_broadcasts_url
        if len(broadcasts_url)==0:
            broadcasts_url=_update_committee_broadcasts_url(comm)
        if len(broadcasts_url)>0:
            videos=_get_committee_videos(broadcasts_url)
            for video in videos:
                _update_committee_mms_video(comm,video)
                    
def download_committees_videos():
    object_type=ContentType.objects.get_for_model(Committee)
    for video in Video.objects.filter(content_type__pk=object_type.id,group='mms'):
        url=video.embed_link
        filename=url.split('/')
        filename=filename[len(filename)-1]
        if os.path.exists(DATA_ROOT+filename):
            print "file already downloaded: "+filename
        else:
            cmd='mimms --resume '+url+' '+DATA_ROOT+filename+'.part'
            os.system(cmd)
            if os.path.exists(DATA_ROOT+filename+'.part'):
                os.rename(DATA_ROOT+filename+'.part',DATA_ROOT+filename)
                print "downloaded "+filename

def upload_committees_videos():
    object_type=ContentType.objects.get_for_model(Committee)
    for video in Video.objects.filter(content_type__pk=object_type.id,group='mms'):
        url=video.embed_link
        filename=url.split('/')
        filename=filename[len(filename)-1]
        if os.path.exists(DATA_ROOT+filename):
            video=_youtube_upload_video(DATA_ROOT+filename,{
                'title':video['title'],
                'published':video['published']
            })

#### Command ####

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--all', action='store_true', dest='all',
            help="runs all the update_videos processes."),
        make_option('--download', action='store_true', dest='download',
            help="download video metadata."),
        make_option('--download-videos', action='store_true', dest='download-videos',
            help="download video data (large files)"),
        make_option('--upload', action='store_true', dest='upload',
            help="uploads the downloaded video data to youtube."),
        make_option('--update', action='store_true', dest='update',
            help="update video metadata"),
        make_option('--with-history', action='store_true', dest='with-history',
            help="download historical data (only relevant with --download option)"),
    )
    help = "Update videos."

    def handle_noargs(self, **options):
        all_options = options.get('all', False)
        download = options.get('download', False)
        download_videos = options.get('download-videos', False)
        upload = options.get('upload', False)
        update = options.get('update', False)
        with_history = options.get('with-history', False)

        if all_options:
            download=True
            download_videos=True
            upload=True
            update=True
        
        if (all([
            not(all_options),
            not(download),
            not(download_videos),
            not(upload),
            not(update),
        ])):
            print "no arguments found. Running update phase. try -h for help."
            update=True
        
                    
        if download:
            print "beginning download phase"
            download_committees_metadata(with_history)
        
        if download_videos:
            print "beginning download-videos phase"
            download_committees_videos()    
        
        if upload:
            print "beginning upload phase"
            upload_committees_videos()
            
        if update:
            print "beginning update phase"
            update_members_about_video()
            update_members_related_videos()
            logger.debug('finished update')

