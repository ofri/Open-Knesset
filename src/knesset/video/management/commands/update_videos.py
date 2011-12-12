# encoding: utf-8

import os
from django.conf import settings
from django.core.management.base import NoArgsCommand
from optparse import make_option
from sub_commands import SubCommand, Timer, Logger, TimeoutException, SubCommandErrorException
from sub_commands.DownloadCommitteesMetadata import DownloadCommitteesMetadata
from sub_commands.DownloadCommitteesVideos import DownloadCommitteesVideos
from knesset.video.management.commands.sub_commands.UpdateMembersAboutVideo import UpdateMembersAboutVideo
from knesset.video.management.commands.sub_commands.UpdateMembersRelatedVideos import UpdateMembersRelatedVideos

class Command(NoArgsCommand,SubCommand):

    def __init__(self):
        NoArgsCommand.__init__(self)
        SubCommand.__init__(self,self)

    DATA_ROOT = getattr(settings, 'DATA_ROOT',
                        os.path.join(settings.PROJECT_ROOT, os.path.pardir, os.path.pardir, 'data'))

    option_list = NoArgsCommand.option_list + (
        make_option('--all', action='store_true', dest='all',
            help="runs all the update_videos processes."),
        make_option('--download', action='store_true', dest='download',
            help="download video data and metadata (same as --download-metadata --download-videos)."),
        make_option('--download-metadata', action='store_true', dest='download-metadata',
            help="download video metadata in preperation for the download-videos phase."),
        make_option('--download-videos', action='store_true', dest='download-videos',
            help="download video data (large files)"),
        make_option('--upload', action='store_true', dest='upload',
            help="uploads the downloaded video data to youtube."),
        make_option('--update', action='store_true', dest='update',
            help="update video metadata"),
        make_option('--with-history', action='store_true', dest='with-history',
            help="download historical data (only relevant with --download options)"),
        make_option('--time-limit', action='store', type='int', dest='time-limit',
            help='limit the process time (in minutes)'),
    )
    help = "Update videos."

    def _set_opts(self,options):
        self._opts={
            'all':options.get('all', False),
            'download':options.get('download', False),
            'download_metadata':options.get('download-metadata', False),
            'download_videos':options.get('download-videos', False),
            'upload':options.get('upload', False),
            'update':options.get('update', False),
            'with_history':options.get('with-history', False),
        }
        
    def _init_opts(self):
        if self._opts['all']:
            self._opts['download']=True
            self._opts['download_videos']=True
            self._opts['upload']=True
            self._opts['update']=True
        if self._opts['download']:
            self._opts['download_metadata']=True
            self._opts['download_videos']=True
        if (all([
            not(self._opts['all']),
            not(self._opts['download']),
            not(self._opts['download_videos']),
            not(self._opts['download_metadata']),
            not(self._opts['upload']),
            not(self._opts['update']),
        ])):
            self._warn("no arguments found. Running update phase. try -h for help.")
            self._opts['update']=True

    def _init_subCommand(self,options):
        if options.get('time-limit', None) is None:
            self.timer=Timer()
        else:
            self.timer=Timer(options.get('time-limit', None)*60)
        self.logger=Logger(options.get('verbosity',1))

    def _run_subCommands(self):
        if self._opts['download_metadata']:
            self._info("beginning download-metadata phase")
            DownloadCommitteesMetadata(self)
            self._check_timer()
        
        if self._opts['download_videos']:
            self._info("beginning download-videos phase")
            DownloadCommitteesVideos(self)
            self._check_timer()
        
        if self._opts['upload']:
            print "beginning upload phase"
            UploadCommitteesVideos(self)
            self._check_timer()
            
        if self._opts['update']:
            self._info("beginning update phase")
            UpdateMembersAboutVideo(self)
            self._check_timer()
            UpdateMembersRelatedVideos(self)
            self._check_timer()

    def handle_noargs(self, **options):
        self._init_subCommand(options)
        self._set_opts(options)
        self._init_opts()
        try:
            self._run_subCommands()
        except TimeoutException:
            self._error("reached the time limit, stopped",no_exception=True)
        except SubCommandErrorException:
            pass
