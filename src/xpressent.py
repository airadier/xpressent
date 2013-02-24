#! /usr/bin/env python

# Copyright 2009, Alvaro J. Iradier
# This file is part of xPressent.
#
# xPressent is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xPressent is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xPressent.  If not, see <http://www.gnu.org/licenses/>.


import pygame
import sys
import os
import config
import remotes
import threading
from pdfmanager import *
from slidemanager import *
from notesmanager import *
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

#User defined pygame events
EVENT_HIDEMOUSE = pygame.USEREVENT + 1

class Screen(object):

    def __init__(self, fullscreen, window_size):
        self.window_size = window_size
        self.size_lock = threading.RLock()
        self.blit_lock = threading.Lock()
        self.surface = self.set_videomode(fullscreen, window_size)
        self.paint_overlay = True

    def set_videomode(self,fullscreen, window_size):
        self.size_lock.acquire()
        self.blit_lock.acquire()
        surface = pygame.display.set_mode(
            pygame.display.list_modes()[0] if fullscreen else window_size,
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE | (pygame.FULLSCREEN if fullscreen else False))
        self.overlay = pygame.Surface(surface.get_size(), flags=RLEACCEL)
        self.overlay.set_colorkey((0,0,0))
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
        self.surface.unlock()
        source.unlock()
        self.surface.blit(source, position)
        self.blit_lock.release()

    def flip(self):
        self.blit_lock.acquire()
        if self.paint_overlay:
            self.surface.blit(self.overlay,(0,0))
        pygame.display.flip()
        self.blit_lock.release()

    def toggle_overlay(self, show = None):
        if show is None:
            self.paint_overlay = not self.paint_overlay
        else:
            self.paint_overlay = show

    def draw(self, from_pos, to_pos):
        pygame.draw.line(self.overlay,
            (255,0,0), from_pos, to_pos, 5)

    def clear_overlay(self):
        self.overlay.fill((0,0,0))
        self.paint_overlay = False

    def acquire(self):
        self.size_lock.acquire()

    def release(self):
        self.size_lock.release()

def run():

    if len(sys.argv) != 2:
        print "Usage: %s xpr_file | pdf_file" % (sys.argv[0],)
        print
        sys.exit(-1)

    xpr_file = os.path.abspath(sys.argv[1])
    if not os.path.exists(xpr_file):
        print "File %s not found" % (xpr_file,)
        print
        sys.exit(-1)

    pygame.init()
    pygame.display.set_caption('xPressent')

    window_size = config.window_size
    fullscreen = config.fullscreen
    screen = Screen(fullscreen, window_size)
    prev_pos = None
    pygame.mouse.set_visible(False)

    try:
        notes = NotesManager(xpr_file)
        pdf_file = notes.get_pdf_file()
        doc = PDFManager(pdf_file, config.quality)
        slide = SlideManager(screen, notes, doc)
    except:
        print sys.exc_info()[1]
        #traceback.print_exc()
        sys.exit(-1)

    while True:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYUP:
            if event.key == 102:
                #F key, toggle fullscreen
                fullscreen = not fullscreen
                screen.set_fullscreen(fullscreen)
                slide.refresh()
            elif event.key in (278, ):
                #Home
                screen.clear_overlay()
                slide.move_home()
            elif event.key in (279, ):
                #End
                screen.clear_overlay()
                slide.move_end()
            elif event.key in (281,275):
                #Next page
                screen.clear_overlay()
                slide.move_next_page()
            elif event.key in (280,276):
                #Previous page
                screen.clear_overlay()
                slide.move_prev_page()
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            elif event.key == 99:
                #'C' Key
                screen.clear_overlay()
                slide.repaint()
            elif event.key == 104:
                #'H' Key
                screen.toggle_overlay()
                slide.repaint()
            else:
                print 'Key', event.key
        elif event.type == pygame.VIDEORESIZE:
            screen.change_size((event.w, event.h))
            slide.refresh()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                prev_pos = event.pos
            elif event.button == 3:
                screen.toggle_overlay()
                slide.repaint()

        elif event.type == pygame.MOUSEMOTION:
            pygame.mouse.set_visible(True)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 3000)
            motions = [event]
            motions.extend(pygame.event.get(pygame.MOUSEMOTION))
            if not prev_pos: prev_pos = event.pos
            repaint = False
            for ev in motions:
                if ev.buttons[0]:
                    if not screen.paint_overlay:
                        screen.clear_overlay()
                    screen.draw(prev_pos, ev.pos)
                    screen.toggle_overlay(True);
                    prev_pos = ev.pos
                    repaint = True
            if repaint or True: slide.repaint()
        elif event.type == EVENT_HIDEMOUSE:
            pygame.mouse.set_visible(False)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 0)

if __name__ == '__main__':
    run()
