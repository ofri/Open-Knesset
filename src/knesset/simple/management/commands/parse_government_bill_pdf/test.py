import glob
import os
import sys
from parse_government_bill_pdf import GovProposal
from parse_government_bill_pdf import readable as d
from util import flatten

def show_one(pdf_filename, show_details=False):
    prop = GovProposal(pdf_filename)
    print prop.to_str(show_details)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        files = sorted(glob.glob('*.pdf'))
    else:
        files = sys.argv[1:]
    for pdf_filename in files:
        if not os.path.exists(pdf_filename):
            print "no such file: %s" % (pdf_filename)
        show_one(pdf_filename, show_details=True)

