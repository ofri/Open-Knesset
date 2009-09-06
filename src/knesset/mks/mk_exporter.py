#!/usr/bin/env python

"""
mk_exporter.py

This file exports Parliament member info into a tab-seperated file.
"""

################################################################################
#   Modules                                                                    #
################################################################################

import mk_info_html_parser as mk    # Parliament member HTML parser.

################################################################################
#   Constants                                                                  #
################################################################################

FILENAME = "blah.tsv"
ENCODING = 'utf8'

################################################################################
#   Methods implementation                                                     #
################################################################################

def export(memberDic):
    """Recieves a key/value dictionary, and writes them to a tab-seperated file.
    """
    f = open(FILENAME, "ab")

    """
    for key, value in memberDic.iteritems():
        f.write(value)
        f.write("\t")
    f.write("\n")
    """

    f.write(memberDic['name'].encode(ENCODING))
    f.write("\t")
    f.write(memberDic['img_link'].encode(ENCODING))
    f.write("\n")
    
    f.flush()
    f.close()

	
################################################################################
#   Main                                                                       #
################################################################################

if __name__ == '__main__': export(mk.MKHtmlParser(100).Dict)
