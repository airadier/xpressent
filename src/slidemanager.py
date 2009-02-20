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
import config
from threading import Thread, Lock
from datetime import datetime
from plugins.IPlugin import fire_event, EVENT_SLIDECHANGE

class SlideManager(object):

    def __init__(self, screen, notes, pdf):
        self.screen = screen
        self.notes = notes
        self.pdf = pdf
        self.current_page = 0
        self.current_slide = None
        self.direction = 1
        self.slide_cache = []
        self.refresh_pending = False
        self.load_thread = None
        self.thread_lock = Lock()
        self.cache_lock = Lock()

        self.update_display()

    def move_to_page(self, page_number):
        if page_number >= self.current_page:
            self.direction = 1
        else:
            self.direction = -1
        self.current_page = page_number

        font = pygame.font.Font(None, 20)
        text = font.render("  %d  " % (self.current_page+1), True, (255,0,0), (0,0,0))
        self.screen.blit(text, (10,10))
        self.screen.flip()

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
        self.cache_lock.acquire()
        self.slide_cache = []
        self.cache_lock.release()

    def add_to_cache(self, page_number, slide):

        self.cache_lock.acquire()
        self.slide_cache.append((page_number, slide))
        if len(self.slide_cache) > config.cache_size:
            del self.slide_cache[0]
        self.cache_lock.release()

    def get_from_cache(self, page_number, no_render=False):

        #Check page is in range
        if page_number < 0 or page_number >= self.pdf.get_num_pages():
            return None

        self.cache_lock.acquire()
        for elem in self.slide_cache:
            page, slide = elem
            if page == page_number:
                self.slide_cache.remove(elem)
                self.slide_cache.append(elem)
                self.cache_lock.release()
                return slide

        self.cache_lock.release()
        if no_render: return None

        self.screen.acquire()
        size = self.screen.get_size()
        slide = self.pdf.render_page(page_number, size)
        #slide = pygame.transform.smoothscale(slide, size)
        self.add_to_cache(page_number, slide)
        self.screen.release()

        return slide

    def notify_preload_finished(self):
        self.thread_lock.acquire()
        self.load_thread = None
        self.thread_lock.release()
        #In case last updated page was removed from cache,
        #or user moved to a new page, repaint again
        if self.refresh_pending \
            or not self.get_from_cache(self.current_page, no_render=True):
            self.update_display()

    def notify_load_finished(self, slide, page):
        #If user didn't change the current page, paint it
        if page == self.current_page and not self.refresh_pending:
            self.repaint(slide)
            notes = self.notes.get_notes(self.current_page)
            fire_event(EVENT_SLIDECHANGE, (self, self.current_page, slide, notes))
            return True
        else:
            self.thread_lock.acquire()
            self.load_thread = None
            self.thread_lock.release()
            self.update_display()
            return False


    def update_display(self):

        self.thread_lock.acquire()
        if self.load_thread:
            self.load_thread.stop()
            self.refresh_pending = True
            self.thread_lock.release()
            return
        self.thread_lock.release()

        self.refresh_pending = False
        self.thread_lock.acquire()
        if self.direction > 0:
            self.load_thread = SlideLoader(self, self.current_page, self.current_page + config.preload)
        else:
            self.load_thread = SlideLoader(self, self.current_page, self.current_page - config.preload)

        self.load_thread.start()
        self.thread_lock.release()


    def refresh(self):
        self.clear_cache()
        self.update_display()

    def repaint(self, slide=None):
        self.screen.acquire()
        if not slide: slide = self.current_slide
        if not slide:
            self.screen.release()
            return
        size = self.screen.get_size()
        slide_size = slide.get_size()
        self.screen.clear()
        self.screen.blit(slide, (
            (size[0] - slide_size[0]) / 2,
            (size[1] - slide_size[1]) / 2))
        self.screen.flip()
        self.current_slide = slide
        self.screen.release()


class SlideLoader(Thread):

    def __init__(self, manager, first_slide, last_slide):
        Thread.__init__(self)
        self.manager = manager
        self.first_slide = first_slide
        self.last_slide = last_slide
        self.daemon = False
        self.running = True

    def stop(self):
        self.running = False


    def run(self):
        #print self.getName(),"Loading slide", self.first_slide
        slide = self.manager.get_from_cache(self.first_slide)
        if not self.manager.notify_load_finished(slide, self.first_slide):
            #print self.getName(),"Aborted"
            return
        #print self.getName(),"Slide loaded"

        if self.last_slide > self.first_slide:
            slides = range(self.first_slide + 1, self.last_slide + 1)
        else:
            slides = range(self.first_slide - 1, self.last_slide - 1, -1)

        #print self.getName(),"Preloading from", slides[0], "to", slides[-1]
        for page in slides:
            if not self.running:
                #print self.getName(),"Aborted"
                self.manager.notify_preload_finished()
                return
            self.manager.get_from_cache(page)
        #print self.getName(),"Load thread done"
        self.manager.notify_preload_finished()


