#encoding: utf-8

from django.test import TestCase
from knesset.video.management.commands.sub_commands.AddVideo import AddVideo

class AddVideo_test(AddVideo):
    
    def __init__(
        self, options, testCase, getMemberObjectReturn, getYoutubeVideosReturn,
        getIsVideoExistsReturn, saveVideoReturn
    ):
        self._testCase=testCase
        self._getMemberObjectReturn=getMemberObjectReturn
        self._getYoutubeVideosReturn=getYoutubeVideosReturn
        self._getIsVideoExistsReturn=getIsVideoExistsReturn
        self._saveVideoReturn=saveVideoReturn
        self.saveVideoLog=[]
        AddVideo.__init__(self,options)
    
    def _getMemberObject(self,**kwargs):
        params=(kwargs['id'],)
        self._testCase.assertIn(params,self._getMemberObjectReturn)
        return self._getMemberObjectReturn[params]
    
    def _getYoutubeVideos(self,**kwargs):
        params=(kwargs['youtube_id_url'],)
        self._testCase.assertIn(params,self._getYoutubeVideosReturn)
        return self._getYoutubeVideosReturn[params]
    
    def _isVideoExists(self,video):
        params=(video['source_id'],)
        self._testCase.assertIn(params,self._getIsVideoExistsReturn)
        return self._getIsVideoExistsReturn[params]
    
    def _saveVideo(self,videoFields):
        params=(videoFields['source_id'],)
        self._testCase.assertIn(params,self._saveVideoReturn)
        self.saveVideoLog.append(videoFields)
        return self._saveVideoReturn[params]

class Options_test():
    
    def __init__(self,testCase,opts):
        self._opts=opts
        self._testCase=testCase
    
    def get(self,varname,default):
        params=(varname,default)
        self._testCase.assertIn(params,self._opts)
        return self._opts[params]

class Member_test():
    pass

class Video_test():
    
    def __init__(self,id):
        self.id=id
        
    def save(self):
        pass

class testAddVideo(TestCase):
    
    testAddVideo=True
    
    def testInvalidParams(self):
        options=Options_test(self,{
            ('video-link',None):None,
            ('object-type',None):None,
            ('object-id',None):None,
            ('is_sticky',False):False,
        })
        getMemberObjectReturn={}
        getYoutubeVideosReturn={}
        getIsVideoExistsReturn={}
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn('you must specify a video link, object type and object id',av.ans)

    def testUnsupportedObjectType(self):
        options=Options_test(self,{
            ('video-link',None):'yyy',
            ('object-type',None):'xxx',
            ('object-id',None):'xxx',
            ('is_sticky',False):False,
        })
        getMemberObjectReturn={}
        getYoutubeVideosReturn={}
        getIsVideoExistsReturn={}
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn('unsupported object type',av.ans)

    def testInvalidYoutubeLink(self):
        options=Options_test(self,{
            ('video-link',None):'http://youtube/video1',
            ('object-type',None):'member',
            ('object-id',None):'1',
            ('is_sticky',False):True,
        })
        getMemberObjectReturn={
            ('1',):Member_test()
        }
        getYoutubeVideosReturn={}
        getIsVideoExistsReturn={}
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn("unable to determine source type from url",av.ans)
    
    def testCantFindYoutubeVideo(self):
        options=Options_test(self,{
            ('video-link',None):'http://youtube/video?v=03aA',
            ('object-type',None):'member',
            ('object-id',None):'1',
            ('is_sticky',False):True,
        })
        getMemberObjectReturn={
            ('1',):Member_test()
        }
        getYoutubeVideosReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):[]
        }
        getIsVideoExistsReturn={}
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn("failed to add the video",av.ans)
        
    def testVideoAlreadyExists(self):
        options=Options_test(self,{
            ('video-link',None):'http://youtube/video?v=03aA',
            ('object-type',None):'member',
            ('object-id',None):'1',
            ('is_sticky',False):True,
        })
        getMemberObjectReturn={
            ('1',):Member_test()
        }
        getYoutubeVideosReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):[{},{},]
        }
        getIsVideoExistsReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):True
        }
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn("failed to add the video",av.ans)

    def testInvalidYoutubeVideoData(self):
        options=Options_test(self,{
            ('video-link',None):'http://youtube/video?v=03aA',
            ('object-type',None):'member',
            ('object-id',None):'1',
            ('is_sticky',False):True,
        })
        getMemberObjectReturn={
            ('1',):Member_test()
        }
        getYoutubeVideosReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):[{},{},]
        }
        getIsVideoExistsReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):False
        }
        saveVideoReturn={}
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertFalse(av.run())
        self.assertIn("failed to add the video",av.ans)

    def testAddYoutubeVideo(self):
        options=Options_test(self,{
            ('video-link',None):'http://youtube/video?v=03aA',
            ('object-type',None):'member',
            ('object-id',None):'1',
            ('is_sticky',False):True,
        })
        getMemberObjectReturn={
            ('1',):Member_test()
        }
        getYoutubeVideosReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):[
                {
                    'embed_url_autoplay':'',
                    'thumbnail480x360':'',
                    'thumbnail90x120':'',
                    'title':'',
                    'description':'',
                    'link':'',
                    'id':'http://gdata.youtube.com/feeds/api/videos/03aA',
                    'published':'',
                },
                {},
            ]
        }
        getIsVideoExistsReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):False
        }
        saveVideoReturn={
            ('http://gdata.youtube.com/feeds/api/videos/03aA',):Video_test(1)
        }
        av=AddVideo_test(
            options, self, getMemberObjectReturn, getYoutubeVideosReturn,
            getIsVideoExistsReturn, saveVideoReturn
        )
        self.assertTrue(av.run())
        
        
        
        
        
        