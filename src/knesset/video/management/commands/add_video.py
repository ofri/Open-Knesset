# encoding: utf-8

from django.core.management.base import NoArgsCommand
from optparse import make_option
from knesset.video.management.commands.sub_commands.AddVideo import AddVideo

class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--video-link',action='store',dest='video-link',
            help="link to the video, use --list-types to see a list of supported link types"),
        make_option('--list-types',action='store_true',dest='list-types',
            help="list supported video link types and formats"),
        make_option('--object-type',action='store',dest='object-type',
            help="set the object type, currently only member is supported"),
        make_option('--object-id',action='store',dest='object-id',
            help="set the object id that the video will be related to"),
        make_option('--sticky',action='store_true',dest='is_sticky',
            help="set the video as sticky"),
    )  

    def handle_noargs(self, **options):
        if options.get('list-types',False):
            print """Supported link formats:
youtube - http://www.youtube.com/watch?v=2sASREICzqY"""
        else:
            av=AddVideo(options)
            av.run()
            print av.ans                

