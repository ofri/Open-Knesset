# encoding: utf-8
"""This file contains some util function to help parse the PDF files,
   found in http://www.knesset.gov.il/laws/heb/template.asp?Type=3
"""

import re,urllib2,subprocess,logging,sys,traceback
from datetime import date
from knesset.utils import clean_string

logger = logging.getLogger("open-knesset.parse_knesset_bill_pdf")

def parse(url):
    """This is the main function that should be used. pass a url of a law PDF to parse
       return value is an array of laws data found
       each law data is a dict with keys 'title', 'references' and 'original_ids'.
       original_ids is an array of original laws ids.
    """
    download_pdf(url)
    pdftotext()
    return parse_pdf_text(url=url)


def pdftotext():
    rc = subprocess.call(['pdftotext', '-enc', 'UTF-8', 'tmp.pdf', 'tmp.txt'])
    if rc:
        logger.error('pdftotext returned error code %d' % rc)


def download_pdf(url,filename=None):
    logger.debug('downloading url %s' % url)
    if not filename:
        filename = 'tmp.pdf'
    f = open(filename,'wb')
    d = urllib2.urlopen(url)
    f.write(d.read())
    f.close()


def parse_pdf_text(filename=None, url=None):
    logger.debug('parse_pdf_text filename=%s url=%s' % (str(filename),
                                                        str(url)))
    if not filename:
        filename = 'tmp.txt'
    f = open(filename,'rt')
    content = f.read()
    d = None
    result = []
    m = re.search('עמוד(.*?)מתפרסמת בזה',content, re.UNICODE | re.DOTALL)
    m = clean_string(m.group(1).decode('utf8'))
    m2 = re.findall('^(הצעת חוק.*?) . '.decode('utf8'), m, re.UNICODE | re.DOTALL | re.MULTILINE)
    m3 = re.findall('^(חוק.*?) . '.decode('utf8'),m, re.UNICODE | re.DOTALL | re.MULTILINE)
    m2.extend(m3)
    for title in m2:
        law = {}
        title = title.replace('\n',' ')
        s = re.search(r'[^\d]\d{2,3}[^\d]',title+' ',re.UNICODE) # find numbers of 2-3 digits
        if s:
            (a,b) = s.span()
            title = title[:a+1] + title[b-2:a:-1] + title[b-1:] # reverse them
        law['title'] = title
        result.append(law)

    count = 0 # count how many bills we found the original_ids for so far
    lines = content.split('\n')
    for line in lines:
        m = re.search('(\d{4,4})[\.|\s](\d+)[\.|\s](\d+)', line)
        if m:
            d = date(int(m.group(1)[::-1]), int(m.group(2)[::-1]), int(m.group(3)[::-1]))

        m = re.search('הצעת חוק מס.*?\w+/\d+/\d+.*?[הועברה|הועברו]'.decode('utf8'), line.decode('utf8'), re.UNICODE)
        if m:
            try:
                result[count]['references'] = line
                m2 = re.findall('\w+/\d+/\d+',line.decode('utf8'), re.UNICODE) # find IDs of original proposals
                result[count]['original_ids'] = [a[-1:0:-1]+a[0] for a in m2] # reverse
                count += 1
            except IndexError:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                logger.error("%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)))
                logger.error('count=%d, len(result)=%d, content = \n%s\n--- end of content' % \
                             (count, len(result), content.decode('utf8')))
    for l in result:
        l['date'] = d
    return result

def parse_pdftxt(filename=None, url=None):
    if not filename:
        filename = 'tmp.txt'
    f = open(filename,'rt')
    lines = f.read().split('\n')
    state = 0
    d = None
    result = []
    law = {}

    for (i,line) in enumerate(lines):
        m = re.search('(\d{4,4})[\.|\s](\d+)[\.|\s](\d+)', line)
        if m:
            d = date(int(m.group(1)[::-1]), int(m.group(2)[::-1]), int(m.group(3)[::-1]))

        if line.find('*')>=0 and line.find('**')==-1:
            if state==0:
                title = lines[i+2].decode('utf8').replace(u'\u202b','')
                if len(title)<=2 or title.find('חוק'.decode('utf8'))<0:
                    try:
                        title = lines[i].decode('utf8').replace(u'\u202b','')
                    except UnicodeDecodeError,e:
                        logger.warn("%s\turl=%s" % (e, url))

                s = re.search(r'[^\d]\d{2,3}[^\d]',title+' ',re.UNICODE) # find numbers of 2-3 digits
                if s:
                    (a,b) = s.span()
                    title = title[:a+1] + title[b-2:a:-1] + title[b-1:] # reverse them
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
                law['original_ids'] = [a[-1:0:-1]+a[0] for a in m] # reverse
                result.append(law)
                law = {}
                state = 0
    for l in result:
        l['date'] = d
    return result
