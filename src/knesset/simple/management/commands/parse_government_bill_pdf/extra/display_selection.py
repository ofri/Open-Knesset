""" Code to look at pdf's and check the text selection mechanism
of poppler. Left here for future reference (not used by any management
command).
"""

import os
import itertools

import gtk
import goocanvas
import gobject

import poppler

import read_gov_law_proposal as gov
import pdftotext_ext as ext

pdf=poppler.document_new_from_file('file://%s/538.pdf'%os.getcwd(),password=None)

def squares(width, height, n_wide, n_high):
    dx = float(width) / n_wide
    dy = float(height) / n_high
    for j in xrange(n_high):
        for i in xrange(n_wide):
            yield (dx*i, dy*j, dx,dy)

def enlarging_square_range(start, height, end_width, n):
    for i in xrange(n+1):
        yield (start[0], start[1], end_width * i/n, height)

def find_middle_at_y(page, start, height, the_end):
    rects = [(start[0], start[1], w, height) for w in [0, the_end]]
    def getlen((x,y,w,h)):
        return len(gov.get_text(page, gov.rect(x, y, w, h)))
    vals = [getlen((x,y,w,h)) for x, y, w, h in rects]
    min_val, max_val = vals
    middle = rects[0]
    for i in xrange(10):
        if vals[0] == vals[1]:
            break
        middle = (start[0], start[1], (rects[0][2]+rects[1][2])/2, height)
        middle_len = getlen(middle)
        if middle_len == vals[1]:
            vals[1], rects[1] = middle_len, middle
        elif middle_len == vals[0]:
            vals[0], rects[0] = middle_len, middle
        else:
            print "not a normal stretch at iteration %s" % i
            return (-1, -1)
    #import pdb; pdb.set_trace()
    return middle[2], i

def find_column_separation(page):
    middles = [find_middle_at_y(page, (0, y)) for y in xrange(0,1000,100)]
    return middles

def map_the_desert((width, height), square_to_text, square_iter, text_offset_iter=None):
    window, canvas = make_widget()
    if text_offset_iter is None:
        text_offset_iter = repeat((0,0))
    texts = []
    for x,y,w,h in square_iter:
        dx, dy = text_offset_iter.next()
        txt = square_to_text(x,y,w,h)
        texts.append(txt)
        rect = goocanvas.Rect(x=x+dx,y=y+dy,width=w,height=h)
        text_widget = goocanvas.Text(text=len(txt), x=x+w/2+dx,y=y+h/2+dy)
        canvas.get_root_item().add_child(rect)
        canvas.get_root_item().add_child(text_widget)
    return texts

def cover1(page, N=10):
    return map_the_desert(page, squares(width, height, N, N))

def stretch(use_ext, page_description, start, height, end_width, N=10):
    if use_ext:
        filename, page_num = page_description
        width, height = get_page(filename, page_num).get_size()
        square_to_text = lambda x, y, w, h, filename=filename, page_num=page_num: ext.pdftotext(filename=filename,first=page_num+1, last=page_num+1, x=x, y=y, w=w, h=h)
    else:
        page = page_description
        width, height = page.get_size()
        square_to_text = lambda x, y, w, h, page=page: pypoppler_text_from_page(page, x, y, w, h)
    return map_the_desert((width, height),
        square_to_text,
        enlarging_square_range(start, height, end_width, N),
        itertools.cycle([(0,-10),(0,10)])
        )

def make_widget():
    w = gtk.Window()
    c = goocanvas.Canvas()
    w.add(c)
    w.show_all()
    return w, c

