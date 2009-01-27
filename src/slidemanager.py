import pygame
import config
from threading import Thread, Lock

class SlideManager(object):

    def __init__(self, screen, pdf):
        self.screen = screen
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
        
        #TODO: Mutex????
        
        #Check page is in range
        if page_number < 0 or page_number >= self.pdf.get_num_pages():
            return None
            
        for elem in self.slide_cache:
            page, slide = elem
            if page == page_number:
                self.slide_cache.remove(elem)
                self.slide_cache.append(elem)
                return slide

        slide = self.pdf.render_page(
            page_number,
            (self.screen.get_width(), self.screen.get_height()))
        slide = pygame.transform.smoothscale(slide,
            (self.screen.get_width(), self.screen.get_height()))
        self.add_to_cache(page_number, slide)
        return slide

    def update_display(self):
        slide = self.get_from_cache(self.current_page)
        self.screen.blit(slide, (0,0))
        pygame.display.flip()

        if config.preload > 0:
            if self.direction > 0:
                preload_thread = SlidePreloader(self, self.current_page + 1, self.current_page + config.preload)
            else:
                preload_thread = SlidePreloader(self, self.current_page - 1, self.current_page - config.preload)
            preload_thread.start()

    def refresh(self):
        self.clear_cache()
        self.update_display()
        
class SlidePreloader(Thread):
    
    def __init__(self, manager, first_slide, last_slide):
        Thread.__init__(self)
        self.manager = manager
        self.first_slide = first_slide
        self.last_slide = last_slide
        
    def run(self):
        print "Preloading from", self.first_slide, "to", self.last_slide
        if self.last_slide > self.first_slide:
            slides = range(self.first_slide, self.last_slide + 1)
        else:
            slides = range(self.first_slide, self.last_slide - 1, -1)
        for page in slides:
            print "Preloading", page,"...",
            self.manager.get_from_cache(page)
            print "done"
 