"""
We don't require poppler at this time - pdftotext and pdfinfo both require
less dependencies and provide the same or better functionality.

But we might later on (when poppler gets to be a better python wrapper,
since it is using the same library that pdftotext and pdfinfo use, and
will have less overhead). So this code is left here for possible future use.

Alon
"""

import os
import poppler
from textutil import reverse_numbers

def text_from_page(page, x, y, w, h):
    return gov.get_text(page, gov.rect(x,y,w,h))

pdf_cache = {}

def get_pdf(filename):
    if filename not in pdf_cache:
        pdf_cache[filename] = poppler.document_new_from_file('file://%s' % os.path.realpath(filename),password=None)
    return pdf_cache[filename]

def get_page(filename, page_num):
    return get_pdf(filename).get_page(page_num)

def get_text(page, rect, style=1):
    return reverse_numbers(unicode(page.get_text(style=style,rect=rect)))

def rect(x, y, w, h):
    rect = poppler.Rectangle()
    rect.x1, rect.x2, rect.y1, rect.y2 = x, x+w, y, y+h
    return rect

def get_whole_page_text(page):
    rect = poppler.Rectangle()
    rect.x1, rect.y1 = 0.0, 0.0
    rect.x2, rect.y2 = page.get_size()
    return get_text(page, rect=rect)

def render_page_to_png(page, filename, width=768, height=1024):
    pixbuf=gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
    page.render_selection_to_pixbuf(width/page.get_size()[0],rotation=0,pixbuf=pixbuf,selection=rect,old_selection=poppler.Rectangle(),style=1,glyph_color=gtk.gdk.Color('#ffffff'),background_color=gtk.gdk.Color('#000000'))
    pixbuf.save(filename,'png');


