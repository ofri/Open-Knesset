# encoding: utf-8

import datetime,traceback,sys,os,re,subprocess,json,io,cgi
import xml.etree.ElementTree as ET
from django.conf import settings

FILE_BASE_PATH="plenum_protocols/"

verbosity=1

def _debug(str):
    global verbosity
    if verbosity>1: print str

def _error(str):
    print str

def _isValidFileForPreview(file):
    return re.search(r"[^.]*$",file).group() == "json"

def _escapenl(txt):
    return cgi.escape(txt).replace("\n","<br/>\n")

def _getSpeakerChildHtml(child):
    t=child['t'].strip()
    if len(t)>0:
        return "<div class='speakertext'>"+_escapenl(t)+"</div>"
    else:
        return ""

def _getTitleChildHtml(child):
    if child['s']==1:
        cls="subtitlespeaker"
        t=child['t'].strip()
        if len(t)==0:
            t=u"(דובר לא ידוע)"
        ihtml="<div class='speakername'>"+_escapenl(t)+"</div>"
        if len(child['c'])>0:
            ihtml+="<div class='speakercontent'>"
            for schild in child['c']:
                ihtml+=_getSpeakerChildHtml(schild)
            ihtml+="</div>"
    else:
        cls="subtitletext"
        t=child['t'].strip()
        ihtml=cgi.escape(t)
    if len(ihtml)>0:
        return "<div class='subtitle "+cls+"'>"+ihtml+"</div>"
    else:
        return ""

def _getTitleHtml(title):
    chtml=""
    contentdiv=''
    for child in title['c']:
        chtml+=_getTitleChildHtml(child)
    if len(chtml)>0:
        contentdiv='<div class="titlecontent">'+chtml+'</div>'
    t=title['t'].strip()
    textdiv=''
    if len(t)>0:
        textdiv='<div class="titletext">'+_escapenl(t)+'</div>'
    return '<div class="title">'+textdiv+contentdiv+'</div>'

def _getHtml(html):
    return """<!doctype html><html><head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        <link href="style.css" rel="stylesheet" type="text/css"/>
        <script src="code.js" type="text/javascript"></script>
    </head>
    <body>
        """+html+"""
    </body>
    </html>"""

def _parsePathDate(path):
    ret=re.search(r"([^/]*)/([^/]*)/([^/]*)$",path)
    return (ret.group(3),ret.group(2),ret.group(1))

def _getAllHtmlEntry(d,m,y,f):
    return "<div class='allhtmlentry'><a href='"+f+"'><span class='allhtmldate'>"+d+"/"+m+"/"+y+"</span> <span class='allhtmlfile'>"+f+"</span></a></div>"

allhtml=None

def _createPreview(root,filename,files):
    _debug('processing '+root+'/'+filename)
    html=""
    with open(root+'/'+filename,'r') as f:
        jsondata=f.read()
    titles=json.loads(jsondata)
    for title in titles:
        html+=_getTitleHtml(title)
    html=_getHtml(html)
    DATA_ROOT = getattr(settings, 'DATA_ROOT')
    fn=DATA_ROOT+FILE_BASE_PATH+'/'+filename+'.html'
    with open(fn,'w') as f:
        f.write(html.encode('utf-8'))
    global allhtml
    (d,m,y)=_parsePathDate(root)
    allhtml+=_getAllHtmlEntry(d,m,y,filename+'.html')
    _debug('wrote html file')

def HtmlPreview(verbosity_level):
    global verbosity
    verbosity=int(verbosity_level)
    DATA_ROOT = getattr(settings, 'DATA_ROOT')
    global allhtml
    allhtml=""
    for root, dirs, files in os.walk(DATA_ROOT+FILE_BASE_PATH):
        for file in files:
            if _isValidFileForPreview(file):
                _createPreview(root,file,files)
    allhtml=_getHtml(allhtml)
    with open(DATA_ROOT+FILE_BASE_PATH+'/index.html','w') as f:
        f.write(allhtml.encode('utf-8'))
    _debug('wrote index html file')

