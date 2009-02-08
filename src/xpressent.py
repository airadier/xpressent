#! /usr/bin/env python

import pygame
import sys
import os
import config
import remotes
import plugins
import threading
from datetime import datetime

from pdfmanager import *
from slidemanager import *
from notesmanager import *
from pygame.locals import *
from events import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

if len(sys.argv) != 2:
    print "Usage: %s xpr_file|pdf_file" % (sys.argv[0],)
    print
    sys.exit(-1)

xpr_file = os.path.abspath(sys.argv[1])
if not os.path.exists(xpr_file):
    print "File %s not found" % (xpr_file,)
    print
    sys.exit(-1)

quality = config.quality

class Screen(object):
    
    
    def __init__(self, fullscreen, window_size):
        self.window_size = window_size
        self.size_lock = threading.RLock() 
        self.blit_lock = threading.Lock()

        self.surface = self.set_videomode(fullscreen, window_size)
    
    def set_videomode(self,fullscreen, window_size):
        self.size_lock.acquire()
        self.blit_lock.acquire()
        surface = pygame.display.set_mode(
            pygame.display.list_modes()[0] if fullscreen else window_size,
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))
        self.blit_lock.release()
        self.size_lock.release()
        return surface


    def set_fullscreen(self, fullscreen):
        self.set_videomode(fullscreen, self.window_size)
        
    def change_size(self, size):
        self.window_size = size
        self.size_lock.acquire()
        self.blit_lock.acquire()
        pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        self.blit_lock.release()
        self.size_lock.release()

    def get_size(self):
        size = (self.surface.get_width(), self.surface.get_height())
        return size

    def clear(self):
        self.surface.fill((0,0,0))

    def blit(self, source, position):
        self.blit_lock.acquire()
        self.surface.blit(source, position)
        self.blit_lock.release()
        
    def flip(self):
        self.blit_lock.acquire()
        pygame.display.flip()
        self.blit_lock.release()


    def acquire(self):
        self.size_lock.acquire()
       
    def release(self):
        self.size_lock.release()

def run():

    pygame.init()
    window_size = config.window_size
    
    fullscreen = config.fullscreen
    screen = Screen(fullscreen, window_size)

    pygame.display.set_caption('xPressent')
    pygame.mouse.set_visible(False)

    try:
        notes = NotesManager(xpr_file)
        pdf_file = notes.get_pdf_file()
        doc = PDFManager(pdf_file, quality)
    except Exception, ex:
        print ex.message
        print
        sys.exit(-1)
    
    slide = SlideManager(screen, notes, doc)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.KEYUP:
            if event.key == 102: #F key
                #Toggle fullscreen
                fullscreen = not fullscreen
                screen.set_fullscreen(fullscreen)
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

            #pygame.event.clear(pygame.KEYUP)

        elif event.type == pygame.VIDEORESIZE:
            screen.change_size((event.w, event.h))
            slide.refresh()
        elif event.type == pygame.MOUSEMOTION:
            pygame.mouse.set_visible(True)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 3000)
        elif event.type == EVENT_HIDEMOUSE:
            pygame.mouse.set_visible(False)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 0)
        else:
            pass
            #print event

if __name__ == '__main__':
    run()
