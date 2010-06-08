# encoding: utf-8
"""This file contains some util function to help parse the PDF files,
   found in http://www.knesset.gov.il/laws/heb/template.asp?Type=3
"""

import re
import urllib2
import subprocess
import logging

logger = logging.getLogger("open-knesset.parse_knesset_bill_pdf")

def parse(url):
    """This is the main function that should be used. pass a url of a law PDF to parse
       return value is an array of laws data found
       each law data is a dict with keys 'title', 'references' and 'original_ids'.
       original_ids is an array of original laws ids.
    """
    download_pdf(url)
    pdftotext()
    return parse_pdftxt(url=url)


def pdftotext():
    rc = subprocess.call(['pdftotext', '-enc', 'UTF-8', 'tmp.pdf', 'tmp.txt'])   
    if rc:
        logger.error('pdftotext returned error code %d' % rc)


def download_pdf(url,filename=None):
    if not filename:
        filename = 'tmp.pdf'
    f = open(filename,'wb')
    d = urllib2.urlopen(url)
    f.write(d.read())
    f.close()    

def parse_pdftxt(filename=None, url=None):
    if not filename:
        filename = 'tmp.txt'
    f = open(filename,'rt')
    lines = f.read().split('\n')
    state = 0
    result = []
    law = {}
    for (i,line) in enumerate(lines):
        if line.find('*')>=0 and line.find('**')==-1:
            if state==0:
                title = lines[i+2].decode('utf8').replace(u'\u202b','')
                if len(title)<=2 or title.find('חוק'.decode('utf8'))<0:
                    try:
                        title = lines[i].decode('utf8').replace(u'\u202b','')
                    except UnicodeDecodeError,e:
                        logger.warn("%s\turl=%s" % (e, url)) 
                law['title'] = title
                state = 1
                continue
            if state==1:                
                for j in range(-2,3):
                    x = lines[i+j].decode('utf8')
                    if re.search('\w+/\d+/\d+', x, re.UNICODE):
                        break
                if not re.search('\w+/\d+/\d+', x, re.UNICODE): # shit...
                    logger.warn("Can't find expected string \w+\d+\d+ in url %s" % url)
                law['references'] = x
                m = re.findall('\w+/\d+/\d+',x, re.UNICODE) # find IDs of original proposals
                law['original_ids'] = [a[-1:0:-1]+a[0] for a in m] # inverse                   
                result.append(law)
                law = {}
                state = 0
    return result
