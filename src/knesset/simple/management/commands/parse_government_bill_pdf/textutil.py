from itertools import chain
import re
from hashlib import md5

superscript = u'\u200F'
digits = set([str(i) for i in xrange(10)])

def fix_superscripts(txt):
    """ Note: call this before reverse_numbers!!
    
    Here's what happens:
    We have the following input to pdftotext
     AAAAA XS DBBB
    What we get is
     AAAAA BBB XS
     D
    So for instance DBBB would be a year number, and we get the most significant
    digit on a separate line. X is the unicode superscript char, and S is the char
    being superscripted.

    Here we fix this, and return the list of superscripts with their location in the
    text.
    """
    superscripts = []
    for i, l in enumerate(txt):
        if superscript in l:
            i_ss = l.find(superscript)
            ss = l[i_ss+1:i_ss+2] # FIXME - this assumes single digit
            # number of superscript should be on next line alone.
            D = txt[i+1].strip()
            txt[i] = txt[i][:i_ss-1] + D + txt[i][i_ss+2:]
            del txt[i+1]
            superscripts.append((i, i_ss, ss))
    return txt, superscripts

def reverse_numbers(s):
    ret = []
    start = 0
    for match in re.finditer('[0-9\.]+', s):
        sl = slice(*match.span())
        ret.append(s[start:sl.start])
        ret.append(reversed(s[sl]))
        start = sl.stop
    ret.append(s[start:])
    return ''.join(chain(*ret))

def sanitize(lines):
    """ remove non text unicode charachters; maybe some of them could be used
    to give hints on parsing?. """
    return [line.replace(u'\u202b','').replace(u'\u202c','').replace(u'\x0c','')
            for line in lines]

def text_block_iter(lines):
    block = []
    for line in lines:
        if line.strip() == '':
            if len(block) > 0:
                yield block
                block = []
            continue
        block.append(line)
    if len(block) > 0:
        yield block

def checksum(lines):
    return md5(''.join(lines)).digest()

def asblocks(lines):
    return list(text_block_iter(lines))

