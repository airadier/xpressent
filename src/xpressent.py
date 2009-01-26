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


class SlideManager(object):

    def __init__(self, pdf):
        self.pdf = pdf
        self.current_page = 0
        self.direction = 1
        self.slide_cache = []

        self.update_display()

    def move_to_page(self, page_number):
        if page_number >= self.current_page:
            self.direction = 1
        else:
            self.direction = -1
        self.current_page = page_number
        self.update_display()

    def move_home(self):
        return self.move_to_page(0)

    def move_next_page(self):
        if self.current_page < self.pdf.get_num_pages() - 1:
            return self.move_to_page(self.current_page + 1)

    def move_prev_page(self):
        if self.current_page > 0:
            return self.move_to_page(self.current_page - 1)

    def move_end(self):
        return self.move_to_page(self.pdf.get_num_pages() - 1)

    def clear_cache(self):
        self.slide_cache = []

    def add_to_cache(self, page_number, slide):
        self.slide_cache.append((page_number, slide))
        if len(self.slide_cache) > config.cache_size:
            del self.slide_cache[0]

    def get_from_cache(self, page_number):
        for elem in self.slide_cache:
            page, slide = elem
            if page == page_number:
                self.slide_cache.remove(elem)
                self.slide_cache.append(elem)
                return slide

        slide = self.pdf.render_page(
            page_number,
            (screen.get_width(), screen.get_height()))
        slide = pygame.transform.smoothscale(slide,
            (screen.get_width(), screen.get_height()))
        self.add_to_cache(page_number, slide)
        return slide

    def update_display(self):
        slide = self.get_from_cache(self.current_page)
        screen.blit(slide, (0,0))
        pygame.display.flip()

        preload_page = self.current_page
        for i in range(config.preload):
            preload_page = preload_page + self.direction
            if preload_page > 0 and preload_page < self.pdf.get_num_pages():
                self.get_from_cache(preload_page)
            else: break

    def refresh(self):
        self.clear_cache()
        self.update_display()

def run():
    global screen

    pygame.init()
    screen = set_videomode(config.fullscreen)
    pygame.display.set_caption('xPressent')
    pygame.mouse.set_visible(False)

    fullscren = config.fullscreen
    doc = PDFManager(pdf_file)
    slide = SlideManager(doc)

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
                slide.refresh()
            elif event.key in (278, ):
                #Home
                slide.move_home()
            elif event.key in (279, ):
                #End
                slide.move_end()
            elif event.key in (281,275):
                #Next page
                slide.move_next_page()
            elif event.key in (280,276):
                #Previous page
                slide.move_prev_page()
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            else:
                print 'Key', event.key

            pygame.event.clear()

        elif event.type == pygame.VIDEORESIZE:
            pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            slide.refresh()
        elif event.type == pygame.MOUSEMOTION:
            pass
        else:
            pass
            #print event

if __name__ == '__main__':
    run()
