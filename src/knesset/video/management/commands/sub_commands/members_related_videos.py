# encoding: utf-8
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
        names=member.all_names
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
