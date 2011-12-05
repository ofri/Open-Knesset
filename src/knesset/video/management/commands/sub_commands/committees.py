# encoding: utf-8

class UploadCommitteesVideos:

    def __init__(self,time_limit):
        start=time.time()
        object_type=ContentType.objects.get_for_model(Committee)
        for video in Video.objects.filter(content_type__pk=object_type.id,group='mms'):
            if time_limit-time.time()-start<=0: break
            url=video.embed_link
            filename=url.split('/')
            filename=filename[len(filename)-1]
            if os.path.exists(DATA_ROOT+filename):
                video=_youtube_upload_video(DATA_ROOT+filename,{
                    'title':video['title'],
                    'published':video['published']
                })

