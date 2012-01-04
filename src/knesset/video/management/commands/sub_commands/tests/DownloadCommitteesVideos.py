#encoding: utf-8

from django.test import TestCase
from knesset.video.management.commands.sub_commands.DownloadCommitteesVideos import DownloadCommitteesVideos

class DownloadCommitteesVideos_test(DownloadCommitteesVideos):
    pass

class testDownloadCommitteesVideos(TestCase):
    
    def testDownloadCommitteesVideos(self):
        self.assertTrue(False)