import config
import pygame
import Image
import cStringIO
from struct import pack, unpack
from pygame.event import Event
from threading import Thread
from plugins.IPlugin import *

PROT_VERSION = 1
PKT_HELLO = 0
PKT_KEYPRESS = 1
PKT_CURRSLIDE = 2
PKT_NEXTSLIDE = 3
PKT_PREVSLIDE = 4
PKT_NOTES = 5


class RemoteBase(Thread):
    """Base class for all remote controllers"""

    def __init__ (self):
        Thread.__init__(self)
        
        # Make the current remote thread a daemon
        self.daemon = True
        # Client list will be empty
        self.clients = []
        # Default client size defaults to 640x480
        self.client_size = (640, 480)
        
        # Set current slide and notes to None
        self.current_slide = None
        self.current_notes = None
        self.slidemanager = None
        self.page_number = None

    def get_aspect_size(self, screen_size, page_size):
        """Calculate a render size that fits in 'screen_size' and keeps the
        aspect ratio of 'page_size'"""
        
        #Calculate page and screen ratios
        page_ratio = float(page_size[0]) / float(page_size[1])
        screen_ratio = float(screen_size[0]) / float(screen_size[1])
        
        if page_ratio >= screen_ratio:
            dest_w = screen_size[0]
            dest_h = screen_size[0] / page_ratio
        else:
            dest_h = screen_size[1]
            dest_w = screen_size[1] * page_ratio

        return int(dest_w), int(dest_h)


    def slide_change(self, slidemanager, page_number, slide, notes, client=None):
        """Event fired when the current slide has changed"""
        if not slidemanager: return
        
        #Scale slide to fit the client with
        slide = pygame.transform.scale(
            slide,
            self.get_aspect_size(self.client_size, slide.get_size()))
        
        #Convert slide to JPEG (use PIL instead of pygame, which needs version >=1.8
        f = cStringIO.StringIO()
        pil_img = Image.fromstring('RGB', slide.get_size(), pygame.image.tostring(slide, 'RGB'))
        pil_img.save(f, 'JPEG', quality=15)
        slide_jpg = f.getvalue()
        f.close()

        #Send current slide JPEG to all clients
        for client in [client] if client else self.clients:
            try:
                self.send(client, pack("!iii", PKT_CURRSLIDE, len(slide_jpg), page_number))
                self.send(client, slide_jpg)
            except IOError:
                pass

        #Send notes to all clients
        for client in [client] if client else self.clients:
            try:
                notes_utf = notes.encode('utf-8')
                self.send(client, pack("!ii", PKT_NOTES, len(notes_utf)))
                self.send(client, notes_utf)
            except IOError:
                pass

        #Save current data for other clients
        self.slidemanager = slidemanager
        self.current_slide = slide
        self.current_notes = notes
        self.page_number = page_number


    def run(self):

        #Register remote as event listener
        register_event_listener(EVENT_SLIDECHANGE, self.slide_change)
        
        if not self.initialize(): return
        
        while True:
            #Wait for a new connection
            client, client_info = self.wait_connection()

            try:
                #When client connects, send HELLO packet, and check versions
                self.send(client, pack("!ii", PROT_VERSION, PKT_HELLO))
                version, = unpack("!i", self.recv(client, 4))
                if version > PROT_VERSION:
                    print "Unsupported client version: %d", version
                    raise IOError
                if unpack("!i", self.recv(client, 4))[0] != PKT_HELLO:
                    print "Unexpected message received"
                    raise IOError

                #Get client screen size
                self.client_size = unpack("!ii", self.recv(client, 8))
                self.clients.append(client)

                #Send current slide to client, firing slide_change event
                self.slide_change(self.slidemanager, self.page_number,
                    self.current_slide, self.current_notes, client = client)

                while True:
                    pkt_type, = unpack("!i", self.recv(client, 4))

                    #If we get the KEYPRESS packet, fire a keypress event
                    if pkt_type == PKT_KEYPRESS:
                        key, = unpack("!i", self.recv(client, 4))
                        pygame.event.post(Event(pygame.KEYUP, key=key, mod=None))

            except IOError,ex:
                print "IOError:", ex
            except Exception,ex:
                print "Error:",ex

            print "Client Disconnected:", client_info

            self.clients.remove(client)
            self.close(client)

        self.shutdown()
        
    def send(self, client, data):
        raise NotImplementedError

    def recv(self, client, bytes):
        raise NotImplementedError
    
    def close(self, client):
        raise NotImplementedError
    
    def initialize(self):
        raise NotImplementedError
    
    def wait_connection(self):
        raise NotImplementedError
        
    def shutdown(self):
        raise NotImplementedError

