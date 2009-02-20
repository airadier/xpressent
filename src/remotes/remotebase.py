import config
import pygame
import Image
import cStringIO
import traceback
from struct import pack, unpack
from pygame.event import Event
from threading import Thread, Lock
from plugins.IPlugin import *

PROT_VERSION = 1
PKT_HELLO = 0
PKT_KEYPRESS = 1
PKT_CURRSLIDE = 2
PKT_NEXTSLIDE = 3
PKT_PREVSLIDE = 4


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
        
        self.thread_lock = Lock()

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


    def slide_change(self, slidemanager, page_number, slide, notes, pclient=None):
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

        self.thread_lock.acquire()
        #Send current slide JPEG to all clients
        for client in [pclient] if pclient else self.clients:
            try:
                client.send_slide(slide_jpg, notes.encode('utf-8'), page_number)
            except IOError:
                #traceback.print_exc()
                #self.clients.remove(client)
                self.close(client)
        self.thread_lock.release()

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

            protocol = XProtocol(self, client, client_info)
            self.clients.append(protocol)
            protocol.start()

        self.shutdown()
        
    def initialize(self):
        raise NotImplementedError
    
    def wait_connection(self):
        raise NotImplementedError
        
    def shutdown(self):
        raise NotImplementedError
    
    def event_connected(self, pclient):
        #Send current slide to client, firing slide_change event
        self.slide_change(self.slidemanager, self.page_number,
            self.current_slide, self.current_notes, pclient = pclient)

    def event_keypress(self, pclient, key):
        pygame.event.post(Event(pygame.KEYUP, key=key, mod=None))

    def event_disconnected(self, pclient, client_info):
        try:
            self.clients.remove(pclient)
        except:
            pass
        print "Client Disconnected:", client_info
        

class XProtocol(Thread):
    
    def __init__(self, remote, client, client_info):
        Thread.__init__(self)
        self.remote = remote
        self.client = client
        self.client_info = client_info
    
    def recv_bytes(self, amount):
        data = ""
        while len(data) < amount:
            data = data + self.client.recv(amount-len(data))
        return data
    
    def send(self, data):
        if not self.client: return 
        return self.client.send(data)
    
    def run(self):
        
        try:
            #When client connects, send HELLO packet, and check versions
            self.client.send(pack("!iii", PROT_VERSION, PKT_HELLO, 0))
            
            version,  = unpack("!i", self.recv_bytes(4))
            if version > PROT_VERSION:
                print "Unsupported client version: %d", version
                raise IOError
                
            hello, len = unpack("!ii", self.recv_bytes(8))
            if  hello != PKT_HELLO:
                print "Unexpected message received"
                raise IOError

            #Get client screen size
            self.client_size = unpack("!ii", self.recv_bytes(len))

            self.remote.event_connected(self)

            while True:
                pkt_type, len = unpack("!ii", self.recv_bytes(8))

                #If we get the KEYPRESS packet, fire a keypress event
                if pkt_type == PKT_KEYPRESS and len == 4:
                    key, = unpack("!i", self.recv_bytes(4))
                    self.remote.event_keypress(self, key)
                else:
                    #Just skip the packet
                    self.recv_bytes(len)

        except IOError:
            print "IOError:"
            traceback.print_exc()
        except SystemError:
            pass
        except Exception:
            print "Error:"
            traceback.print_exc()

        try:
            self.close(self.client)
            self.client = None
        except:
            pass
            
        self.remote.event_disconnected(self, self.client_info)

        
    def send_slide(self, slide_jpg, notes_utf, page_number):
        self.send(pack("!iii", PKT_CURRSLIDE, len(slide_jpg) + len(notes_utf) + 8, page_number))
        self.send(pack("!i", len(slide_jpg)))
        self.send(slide_jpg)
        self.send(pack("!i", len(notes_utf)))
        self.send(notes_utf)

 