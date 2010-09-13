# -*- coding: utf-8 -*-
from urllib import urlopen
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
from tempfile import TemporaryFile

def rtf(url):
    '''
    gets the url of the rtf file, and (tries to) return an xhtml version of it.
    returns False if couldn't convert.
    '''
    remote = urlopen(url)
    data = remote.read()
    remote.close()
    temp = TemporaryFile()
    temp.write(data)
    temp.seek(0)
    try:
        doc = Rtf15Reader.read(temp)
        xhtml = XHTMLWriter.write(doc, pretty=True).read()
    except:
        xhtml = False
    temp.close()
    return xhtml
