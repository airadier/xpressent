#! /usr/bin/env python

#Settings
fullscreen = False
window_size = (800,600)
quality = 100

import pygame
from pygame.locals import *
import cairo
import poppler
import cStringIO
import sys
import os


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

PDFFILE = os.path.abspath(sys.argv[1])

def set_videomode(fullscreen):
	return pygame.display.set_mode(
	    pygame.display.list_modes()[0] if fullscreen else window_size,
	    pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))

#Render to file
def render_page(page_num, size):
    page = doc.get_page(page_num)
    page_w, page_h = page.get_size()
    ratio = page_w/page_h
    if ratio >= 1.0:
        dest_x = size[0]
        dest_y = size[1] / ratio
    else:
        dest_y = size[1]
        dest_x = size[1] * ratio   
    scale_x = (size[0]*quality/100)/page_w
    scale_y = (size[1]*quality/100)/page_h
    img = cairo.ImageSurface(cairo.FORMAT_RGB24,size[0]*quality/100,size[1]*quality/100)
    context = cairo.Context(img)
    context.scale(scale_x, scale_y)
    context.set_source_rgb(1.0, 1.0, 1.0)
    context.rectangle(0, 0, page_w, page_h)
    context.fill()
    page.render(context)
    f = cStringIO.StringIO()
    img.write_to_png(f)
    f.seek(0)
    return pygame.image.load(f, 'img.png');

def redraw():
   slide = render_page(current_page, (screen.get_width(), screen.get_height()))
   img2 = pygame.transform.smoothscale(slide, (screen.get_width(), screen.get_height()))
   screen.blit(img2, (0,0))
   pygame.display.flip()

def input(): 
    global current_page
    global fullscreen
    global window_size

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT: 
            sys.exit(0) 
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.KEYUP:
            pygame.event.clear()
            if event.key == 102: #F key
                #Toggle fullscreen
                fullscreen = not fullscreen
                set_videomode(fullscreen)		
                redraw()
            elif event.key in (281,275):
                #Next page
                current_page = current_page + 1
                if current_page >= doc.get_n_pages(): current_page = doc.get_n_pages()-1
                redraw()
            elif event.key in (280,276):
                #Previous page
                slide = None
                current_page = current_page - 1
                if current_page < 0: current_page = 0
                redraw()
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            else:
                print 'Key', event.key
        elif event.type == pygame.VIDEORESIZE:
            window_size = (event.w, event.h)
            pygame.display.set_mode(window_size, pygame.RESIZABLE)
            print "Redraw", window_size
            redraw()
        elif event.type == pygame.MOUSEMOTION:
            pass
        else:
            pass 
            #print event 


def run():
    global current_page
    global doc
    global screen
    
    pygame.init()

    screen = set_videomode(fullscreen)
    pygame.display.set_caption('xPressent')
    pygame.mouse.set_visible(True)

    doc = poppler.document_new_from_file('file://%s' % PDFFILE, None)
    current_page = 0
    
    redraw()
    
    while True:
        input()

if __name__ == '__main__':
    run()
