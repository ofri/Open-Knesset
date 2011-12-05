#encoding: utf-8

from django.test import TestCase
from knesset.video.management.commands.sub_commands import SubCommand, SubCommandErrorException, Timer
import time

class testSubCommand(TestCase):

    def test(self):
        class MySubCommand(SubCommand):
            def __init__(self,command,test):
                SubCommand.__init__(self,command)
                test.assertEquals(self._get_data_root(),'the data root')
                test.assertEquals(self._get_opt('opt name'),'opt value')
                ok=False
                try:
                    self._check_timer()
                except MyTimerException:
                    ok=True
                test.assertTrue(ok)
                test.assertEqual(self._timer_remaining(),92837745)
                self._debug('debug')
                self._info('info')
                self._warn('warn')
                ok=False
                try:
                    self._error('error')
                except SubCommandErrorException:
                    ok=True
                test.assertTrue(ok)
                self._error('error no ecception',no_exception=True)
                test.assertEqual(self.command.logger._log,[
                    ('debug', 'debug'),
                    ('info', 'info'), 
                    ('warn', 'warn'), 
                    ('error', 'error'), 
                    ('error', 'error no ecception')
                ])
        class MyTimerException:
            pass
        class MyTimer:
            remaining=92837745
            def check(self):
                raise MyTimerException
        class MyLogger:
            _log=[]
            def log(self,msgtype,msg):
                self._log.append((msgtype,msg))
        class MyCommand:
            DATA_ROOT='the data root'
            _opts={'opt name':'opt value'}
            timer=MyTimer()
            logger=MyLogger()
            pass
        command=MyCommand()
        MySubCommand(command,self)
        
class testTimer(TestCase):
    
    def testNoLimit(self):
        start=time.time()
        t=Timer()
        
        