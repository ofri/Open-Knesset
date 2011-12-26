# encoding: utf-8

import os
from knesset.video.management.commands.sub_commands import SubCommand
from django.contrib.contenttypes.models import ContentType
from knesset.committees.models import Committee
from knesset.video.models import Video
import knesset.video.utils.mms as mms

class DownloadCommitteesVideos(SubCommand):
	
	def __init__(self,command):
		SubCommand.__init__(self,command)
		for video in self._getVideosToDownload():
			self._check_timer()
			url=video.embed_link
			self._debug(url)
			filename=self._getFilenameFromUrl(url)			
			if self._isAlreadyDownloaded(filename):
				self._debug("file already downloaded: "+filename)
				continue
			else:
				self._debug('downloading: '+filename)
				partfilename=self._get_data_root()+filename+'.part'
				streamsize=mms.get_size(url)
				self._debug('streamsize = '+str(streamsize))
				mins_remaining=round(self._timer_remaining()/60)
				if os.path.exists(partfilename):
					filesize=os.path.getsize(partfilename)
					if filesize<streamsize:
						self._debug('mms resume download')
						mms.resume_download(url,partfilename,mins_remaining)
				else:
					self._debug('mms download')
					mms.download(url,partfilename,mins_remaining)
				self._debug('done')
				self._check_timer()
				filesize=os.path.getsize(partfilename)
				if filesize==streamsize:
					os.rename(partfilename,filename)
					self._debug("finished downloading: "+filename)

	def _getFilenameFromUrl(self,url):
		filename=url.split('/')
		filename=filename[len(filename)-1]
		return filename

	def _getVideosToDownload(self):
		object_type=ContentType.objects.get_for_model(Committee)
		return Video.objects.filter(content_type__pk=object_type.id,group='mms')
	
	def _isAlreadyDownloaded(self,filename):
		return os.path.exists(self._get_data_root()+filename)
