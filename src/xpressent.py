#! /usr/bin/env python

import pygame
from pygame.locals import *
import cairo
import poppler
import cStringIO
import sys
import os
import config

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

if len(sys.argv) != 2:
    print "Usage: %s pdf_file" % (sys.argv[0],)
    print
    sys.exit(-1)

pdf_file = os.path.abspath(sys.argv[1])
if not os.path.exists(pdf_file):
    print "File %s not found" % (pdf_file,)
    print
    sys.exit(-1)

fullscreen = config.fullscreen
quality = config.quality

def set_videomode(fullscreen):
    return pygame.display.set_mode(
        pygame.display.list_modes()[0] if fullscreen else config.window_size,
        pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))

class PDFManager(object):

    def __init__(self, pdf_file):
        try:
            self.doc = poppler.document_new_from_file('file://%s' % pdf_file, None)
        except Exception, ex:
            print ex.message
            print
            sys.exit(-1)

    def get_num_pages(self):
        return self.doc.get_n_pages()

    def render_page(self, page_num, size):

        page = self.doc.get_page(page_num)
        page_w, page_h = page.get_size()

        render_w = int(size[0] * quality)
        render_h = int(size[1] * quality)

        if config.keep_aspect:
	        #Calculate and compare
	        page_ratio = float(page_w) / float(page_h)
	        screen_ratio = float(size[0]) / float(size[1])
        	if page_ratio >= screen_ratio:
        		dest_w = render_w
        		dest_h = render_w / page_ratio
        	else:
        		dest_h = render_h
        		dest_w = render_h * page_ratio
        else:
        	dest_w, dest_h = render_w, render_h

        img = cairo.ImageSurface(cairo.FORMAT_RGB24, render_w, render_h)
        context = cairo.Context(img)
        context.translate(
			int((render_w - dest_w)/2),
			int((render_h - dest_h)/2))
        context.scale(dest_w/page_w, dest_h/page_h)
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, page_w, page_h)
        context.fill()
        page.render(context)
        f = cStringIO.StringIO()
        img.write_to_png(f)
        f.seek(0)
        return pygame.image.load(f, 'img.png');


def redraw(doc, page):
   slide = doc.render_page(page, (screen.get_width(), screen.get_height()))
   img2 = pygame.transform.smoothscale(slide, (screen.get_width(), screen.get_height()))
   screen.blit(img2, (0,0))
   pygame.display.flip()


def run():
    global current_page
    global screen

    pygame.init()
    screen = set_videomode(config.fullscreen)
    pygame.display.set_caption('xPressent')
    pygame.mouse.set_visible(False)

    fullscren = config.fullscreen
    doc = PDFManager(pdf_file)
    current_page = 0

    redraw(doc, current_page)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.KEYUP:
            if event.key == 102: #F key
                global fullscreen
                #Toggle fullscreen
                fullscreen = not fullscreen
                set_videomode(fullscreen)
                redraw(doc, current_page)
            elif event.key in (278, ):
                #Home
                current_page = 0
                redraw(doc, current_page)
            elif event.key in (279, ):
                #End
                current_page = doc.get_num_pages() - 1
                redraw(doc, current_page)
            elif event.key in (281,275):
                #Next page
                current_page = current_page + 1
                if current_page >= doc.get_num_pages(): current_page = doc.get_num_pages()-1
                redraw(doc, current_page)
            elif event.key in (280,276):
                #Previous page
                slide = None
                current_page = current_page - 1
                if current_page < 0: current_page = 0
                redraw(doc, current_page)
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            else:
                print 'Key', event.key

            pygame.event.clear()

        elif event.type == pygame.VIDEORESIZE:
            pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            redraw(doc, current_page)
        elif event.type == pygame.MOUSEMOTION:
            pass
        else:
            pass
            #print event

if __name__ == '__main__':
    run()
