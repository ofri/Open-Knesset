#!/usr/bin/python
import os
import subprocess
from string import uppercase
import sys

from textutil import asblocks, sanitize

DEBUG=False

def which(x):
    for p in os.environ['PATH'].split(':'):
        path = os.path.join(p, x)
        if os.path.exists(path):
            return path
    return None

def firstl(f, it, default):
    for x in it:
        t = x() if callable(x) else x
        if f(t):
            return t
    t = default() if callable(default) else default
    return t

mod_path = os.path.dirname(sys.modules[__name__].__file__)
if mod_path == '': mod_path = '.'

def local_or_system(toolname):
    return firstl(os.path.exists,
        [os.path.join(mod_path, '..', '..', '..', '..', '..', '..',
                      'parts', 'poppler', 'bin', toolname),
         os.path.join(mod_path, toolname)], lambda: which(toolname))

PDFTOTEXT=local_or_system('pdftotext')
PDFINFO=local_or_system('pdfinfo')

def pdftotext_version():
    p = subprocess.Popen(executable=PDFTOTEXT, args=[PDFTOTEXT, '-v'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    major, minor, patchlevel = map(lambda x,y:y if x is None else x,p.stderr.readlines()[0].strip().split()[-1].split('.'),[0]*3)
    p.kill()
    return major, minor, patchlevel

PDFTOTEXT_VERSION = pdftotext_version()

if DEBUG:
    print "pdftotext from %s, version %s" % (PDFTOTEXT, str(PDFTOTEXT_VERSION))
    print "pdfinfo from %s" % PDFINFO

def pdftotext_version_pass():
    major,minor,patch_level = PDFTOTEXT_VERSION
    major,minor = int(major),int(minor)
    return (major >= 1) or ((major == 0) and (minor >= 14))

def capture_output(args):
    return subprocess.Popen(args, stdout=subprocess.PIPE).stdout.readlines()

def pdftotext(filename, first=None, last=None, x=0, y=0, w=0, h=0):
    params = []
    if first is not None:
        params.extend(['-f %s' % first])
    if last is not None:
        params.extend(['-l %s' % last])
    args = ("%s %s -x %d -y %d -W %d -H %d %s -" % (PDFTOTEXT,
            ' '.join(params), x, y, w, h, filename)).split()
    output = capture_output(args)
    return sanitize([unicode(l,'utf8') for l in output])

def camel_to_lower_case(s):
    t = ''.join('_' if c == ' ' else ('_'+c.lower() if c in uppercase else c) for c in s)
    if t[0] == '_': return t[1:]
    return t

def pdfinfo(filename):
    """ Example output of pdfinfo:
Creator:        Adobe InDesign CS2 (4.0.2)
Producer:       Adobe PDF Library 7.0
CreationDate:   Sun Jul  4 13:09:27 2010
ModDate:        Sun Jul  4 13:09:30 2010
Tagged:         no
Pages:          2
Encrypted:      no
Page size:      481.89 x 680.315 pts
File size:      118581 bytes
Optimized:      yes
PDF version:    1.4
    """
    class PdfInfo(object):
        def __str__(self):
            return 'PdfInfo: %s: %s, %s, %s' % (
                self.filename, self.pages, self.file_size, self.mod_date)
        __repr__ = __str__
    pdfinfo = PdfInfo()
    pdfinfo.filename = filename
    numbers = set('pages file_size'.split())
    def convert(k, v):
        if k in numbers: return int(v.split()[0])
        return v
    data = [(k, convert(k, v.strip())) for k, v in
            ((camel_to_lower_case(k), v.strip()) for k,v in
            (l.split(':',1) for l in capture_output([PDFINFO, filename])))]
    pdfinfo.__dict__.update(data)
    return pdfinfo

def isempty(filename, x=0, y=0, W=0, H=0):
    return len(asblocks(filename, x, y, W, H)) == 0

def num_blocks(filename, x=0, y=0, W=0, H=0):
    return len(asblocks(filename, x=x,y=y,W=W,H=H))

if __name__ == '__main__':
    # Test code - not used
    filename = '538.pdf'
    fulltext = asblocks(filename)
    texts = [pdftotext(filename, x=x,W=1000) for x in xrange(100)]
    checksums = [checksum(filename, x=x, W=1000) for x in xrange(100)]
    for i in xrange(len(checksums)-1):
        if checksums[i] != checksums[i+1]:
            print "change at %s" % i

