#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
import urllib
from BeautifulSoup import BeautifulSoup

GOVT_INFO_PAGE = r"http://www.knesset.gov.il/mk/heb/MKIndex_Current.asp?view=4";
def parse_mk_govt_roles():
    info_dict = {}
    soup = BeautifulSoup(urllib.urlopen(GOVT_INFO_PAGE).read().decode('windows-1255').encode('utf-8'))
    tags = soup.findAll(lambda tag: tag.name == 'div' and tag.has_key('class') and ((tag['class']=='MKIconM') or (tag['class']=='MKIconF')))
    for tag in tags:
        mk_id = tag.first().get('href').split('=')[1]
        mk_roles = tag.find('span').contents[0]
        info_dict[mk_id] = mk_roles
    return info_dict

KNESSET_INFO_PAGE = r"http://www.knesset.gov.il/mk/heb/MKIndex_Current.asp?view=7";
V1 = 'ועדת '
V2 = 'ועדה '
PREFIX = 'יו"ר '.decode('utf8')
def parse_mk_knesset_roles():
    info_dict = {}
    soup = BeautifulSoup(urllib.urlopen(KNESSET_INFO_PAGE).read().decode('windows-1255').encode('utf-8'))
    tags = soup.findAll(lambda tag:tag.name=='tr' and tag.first().has_key('class') and ((tag.first()['class']=='MKIconM') or (tag.first()['class']=='MKIconF')))
    for tag in tags:
        t = str(tag.find('a',{'style':"color:Black;"}).contents[0])
        if (t.find(V1)>=0) or (t.find(V2)>=0):    
            mk_id = tag.find('a').get('href').split('=')[1]
            mk_roles = PREFIX + tag.find('a',{'style':"color:Black;"}).contents[0]
            info_dict[mk_id] = mk_roles
    return info_dict

