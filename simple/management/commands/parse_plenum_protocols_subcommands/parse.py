# encoding: utf-8

import datetime,traceback,sys,os,re,subprocess
from django.conf import settings

FILE_BASE_PATH="plenum_protocols/"

verbosity=1

def _debug(str):
    global verbosity
    if verbosity>1: print str

def _isAlreadyParsed(file,files):
    return file+".json" in files

def _isValidFileForParsing(file):
    return re.search(r"[^.]*$",file).group() == "doc"

def _parsePathDate(path):
    ret=re.search(r"([^/]*)/([^/]*)/([^/]*)$",path)
    return (ret.group(3),ret.group(2),ret.group(1))

def _getJsonFile(file):
    subprocess.call('/usr/bin/antiword -x db '+file+' > '+file+'.xml')

def _parseFile(root,file,files):
    _debug('_parseFile '+root+'/'+file)
    if not file+'.awdb.xml' in files:
        cmd='antiword -x db '+root+'/'+file+' > '+root+'/'+file+'.awdb.xml.tmp'
        _debug(cmd)
        subprocess.call(cmd,shell=True)
        os.rename(root+'/'+file+'.awdb.xml.tmp',root+'/'+file+'.awdb.xml')
    #if _isAlreadyParsed(file,files):
        #_debug('already parsed: '+file)
    #elif _isValidFileForParsing(file):
        #day,month,year=_parsePathDate(root)
        #_debug('parsing: '+file+' ('+day+'/'+month+'/'+year+')')
        #jsondata=_getJsonFile(root+file)
    #else:
        #_debug('invalid file for parsing: '+file)

def Parse(verbosity_level):
    global verbosity
    verbosity=int(verbosity_level)
    DATA_ROOT = getattr(settings, 'DATA_ROOT')
    for root, dirs, files in os.walk(DATA_ROOT+FILE_BASE_PATH):
        for file in files:
            if _isValidFileForParsing(file):
                _parseFile(root,file,files)
