#! /usr/bin/env python

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

pygame.init()
fullscreen = False
window_size = (800,600)
quality = 100
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))
pygame.display.set_caption('Presenter')
pygame.mouse.set_visible(True)


doc = poppler.document_new_from_file('file://%s' % PDFFILE, None)
current_page = 0

#Render to file
def render_page(page_num, size):
	page = doc.get_page(page_num)
	page_w, page_h = page.get_size()
	img = cairo.ImageSurface(cairo.FORMAT_RGB24,size[0],size[1])
	context = cairo.Context(img)
        context.scale(size[0]/page_w, size[1]/page_h)
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
            #TODO: Toggle fullscreen
            fullscreen = not fullscreen
            screen = pygame.display.set_mode(
               (1680,1050) if fullscreen else window_size,
               pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))
            #pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
            redraw()
         elif event.key in (281,275): #Next page
            current_page = current_page + 1
            if current_page >= doc.get_n_pages(): current_page = doc.get_n_pages()-1
            redraw()
         elif event.key in (280,276): #Next page
            slide = None
            current_page = current_page - 1
	    if current_page < 0: current_page = 0
            redraw()
	 elif event.key == 27: #Escape key
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

redraw()

while True:
	input()


