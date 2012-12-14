import difflib
import re

def split(txt):
    l = re.split('\W+', txt, flags=re.UNICODE)
    if l[-1] == u'':
        l.pop()
    return l


def fuzzy_match(str, txt):
    l = split(txt)
    step =  len(split(str))

    for i in xrange(len(l)):
        t = ' '.join(l[i:i + step])
        if difflib.SequenceMatcher(None, str, t).ratio() >= 0.6:
            return True

    return False