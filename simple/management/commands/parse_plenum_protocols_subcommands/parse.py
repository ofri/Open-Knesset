# encoding: utf-8

import datetime,traceback,sys,os,re,subprocess,json,io
import xml.etree.ElementTree as ET
from django.conf import settings

FILE_BASE_PATH="plenum_protocols/"

verbosity=1

def _debug(str):
    global verbosity
    if verbosity>1: print str

def _error(str):
    print str

def _isValidFileForParsing(file):
    return re.search(r"[^.]*$",file).group() == "doc"

def _parsePathDate(path):
    ret=re.search(r"([^/]*)/([^/]*)/([^/]*)$",path)
    return (ret.group(3),ret.group(2),ret.group(1))

def _parseParaElement(para):
    isBold=False
    if para.find('emphasis') is not None:
        isBold=True
    txt=''
    for subtext in para.itertext():
        txt+=subtext
    return (isBold,txt)

def _parseParaText(para,isBold):
    t='text'
    if isBold and re.search(r":[\s]*$",para) is not None:
        # bold + ends with a colod
        t='speaker'
    elif isBold:
        t='title'
    return t

titles=None

def _parsePara(txt,t):
    global titles
    if titles is None:
        titles=[]
        if t=='speaker':
            titles.append({u't':u'',u'c':[
                {u't':txt,u'c':[],u's':1}
            ]})
        elif t=='title':
            titles.append({u't':txt,u'c':[]})
        else:
            titles.append({u't':'',u'c':[
                {u't':txt,u's':0}
            ]})
    elif t=='title':
        titles.append({u't':txt,u'c':[]})
    else:
        title=titles[len(titles)-1]
        children=title['c']
        if t=='speaker':
            children.append({u't':txt,u'c':[],u's':1})
        elif len(children)==0:
            children.append({u't':txt,u's':0})
        elif children[len(children)-1]['s']==1:
            children[len(children)-1]['c'].append({u't':txt})
        else:
            children.append({u't':txt,u's':0})

def _parseFile(root,file,files):
    _debug('_parseFile '+root+'/'+file)
    if not os.path.exists(root+'/'+file+'.json'):
        if not file+'.awdb.xml' in files:
            cmd='antiword -x db '+root+'/'+file+' > '+root+'/'+file+'.awdb.xml.tmp'
            _debug(cmd)
            subprocess.call(cmd,shell=True)
            os.rename(root+'/'+file+'.awdb.xml.tmp',root+'/'+file+'.awdb.xml')
            _debug('wrote xml file')
        if os.path.exists(root+'/'+file+'.awdb.xml'):
            tree=ET.parse(root+'/'+file+'.awdb.xml')
            global titles
            titles=None
            for para in tree.getroot().iter('para'):
                (isBold,txt)=_parseParaElement(para)
                t=_parseParaText(txt,isBold)
                _parsePara(txt,t)
            jsdata=json.dumps(titles)
            with io.open(root+'/'+file+'.json.tmp', 'w') as outfile:
                outfile.write(unicode(jsdata))
            os.rename(root+'/'+file+'.json.tmp',root+'/'+file+'.json')
            _debug('wrote json file')
        else:
            _error('unexpected error, cannot find file '+root+'/'+file+'.awdb.xml')
    else:
        _debug('file already parsed to json')

def Parse(verbosity_level):
    global verbosity
    verbosity=int(verbosity_level)
    DATA_ROOT = getattr(settings, 'DATA_ROOT')
    for root, dirs, files in os.walk(DATA_ROOT+FILE_BASE_PATH):
        for file in files:
            if _isValidFileForParsing(file):
                _parseFile(root,file,files)
