#! /usr/bin/env python

import pygame
import sys
import threading
import cStringIO
import socket
import os
from struct import pack, unpack
from pygame.locals import *
from pygame.event import Event
from events import *
from bluetooth import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

UUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41"

PROT_VERSION = 1
PKT_HELLO = 0
PKT_KEYPRESS = 1
PKT_CURRSLIDE = 2
PKT_NEXTSLIDE = 3
PKT_PREVSLIDE = 4
PKT_NOTES = 5


class Screen(object):

    def __init__(self):
        self.blit_lock = threading.Lock()
        self.surface = self.set_videomode()

    def set_videomode(self):
        self.blit_lock.acquire()
        
        surface = pygame.display.set_mode((800,480))
        #surface = pygame.display.set_mode(
        #    pygame.display.list_modes()[0],
        #    pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)
        self.blit_lock.release()
        return surface

    def get_size(self):
        size = (self.surface.get_width(), self.surface.get_height())
        return size

    def blit(self, source, position):
        self.blit_lock.acquire()
        self.surface.blit(source, position)
        self.blit_lock.release()

    def flip(self):
        self.blit_lock.acquire()
        pygame.display.flip()
        self.blit_lock.release()

    def clear(self):
        self.surface.fill((0,0,0))


class BaseClient(threading.Thread):
    
    def __init__(self, args, screen):
        threading.Thread.__init__(self)
        self.daemon = True
        self.screen = screen
        self.slide = None
        self.show_notes = False
        self.font = None
        self.font_size = 40
        self.args = args

    def repaint_slide(self):
        if self.show_notes:
            self.slide.set_alpha(30)
        else:
            self.slide.set_alpha(255)

        self.screen.clear()
        size = self.screen.get_size()
        slide_size = self.slide.get_size()
        self.screen.blit(self.slide,(
            (size[0]-slide_size[0])/2,
            (size[1]-slide_size[1])/2))
        
        if self.show_notes: self.paint_notes()
            
        self.screen.flip()

    def paint_notes(self):
        #TODO: Improve
        font = pygame.font.SysFont("Helvetica, Sans, Arial", size=self.font_size)
        y = 30
        x = 30
        for line in self.notes.split('\n'):
            surf = font.render(line,True, (255,255,255))
            self.screen.blit(surf, (x,y))
            y = y + font.get_linesize()
        print self.notes

    def toggle_notes(self):
        self.show_notes = not self.show_notes
        self.repaint_slide()

    def read_bytes(self, length):
        read = ""
        while len(read) < length:
            read = read + self.recv(length - len(read))
        return read

    def decrease_font(self):
        self.font_size = self.font_size - 5
        self.repaint_slide()

    def increase_font(self):
        self.font_size = self.font_size + 5
        self.repaint_slide()

    def quit(self):
        pygame.event.post(Event(pygame.QUIT))

    def send_keypress(self, keycode):
        self.send(pack("!ii", PKT_KEYPRESS, keycode))

    def run(self):
        
        try:
            if not self.connect():
                self.quit()
                return
        except Exception, ex:
            print ex
            self.quit()
            
        size = self.screen.get_size()
        self.send(pack("!iiii", PROT_VERSION, PKT_HELLO, size[0], size[1]))
        version, = unpack("!i", self.recv(4))
        if version > PROT_VERSION:
            print "Unsupported server version: %d", version
            sys.exit(-1)
        if unpack("!i", self.recv(4))[0] != PKT_HELLO:
            print "Unexpected packet received"
            sys.exit(-1)

        
        while True:
            pkt_type, = unpack("!i", self.sock.recv(4))
            if pkt_type == PKT_NOTES:
                notes_len, = unpack("!i", self.recv(4))
                self.notes = str.decode(self.read_bytes(notes_len),'utf-8')
                self.repaint_slide()
            elif pkt_type == PKT_CURRSLIDE:
                slide_len, page_number = unpack("!ii", self.sock.recv(8))
                slide_jpg = self.read_bytes(slide_len)
                f = cStringIO.StringIO()
                f.write(slide_jpg)
                f.seek(0)
                self.slide = pygame.image.load(f, 'img.jpg')
                f.close()
                self.repaint_slide()

    def connect(self):
        raise NotImplementedError

    def recv(self, size):
        raise NotImplementedError
    
    def send(self, data):
        raise NotImplementedError
    

class BluetoothClient(BaseClient):
    pass


class SocketClient(BaseClient):
    
    def connect(self):
        if len(self.args) != 2:
            print
            print "Usage: %s host:port" % (os.path.basename(self.args[0]),)
            print "\n   No address specified!"
            return False
        else:
            addr = self.args[0]
            host, port = self.args[1].split(':')
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))
            
        return True

    def recv(self, size):
        return self.sock.recv(size)
    
    def send(self, data):
        return self.sock.send(data)




def run():

    pygame.init()

    #if len(sys.argv) != 2:
    #    print
    #    print "Usage: %s xpressent_addr" % (sys.argv[0],)
    #    print "No address specified, searching in all nearby devices..."
    #    sys.exit(-1)
    #    addr = None
    #else:
    #    addr = sys.argv[1]
    #    print "Searching Xpressent service in addr %s..." % addr

    #service_matches = find_service(uuid = UUID, address = addr)
    #if len(service_matches) == 0:
    #    print "Xpressent service not found"
    #    sys.exit(-1)

    #first_match = service_matches[0]
    #print "Connection to %s at %s" % (
    #    first_match['name'],
    #    first_match['host'])


    #sock = BluetoothSocket(RFCOMM)
    #sock.connect((first_match['host'], first_match['port']))

    screen = Screen()

    client = SocketClient(sys.argv, screen)
    client.start()

    pygame.display.set_caption('xPressent Remote')
    pygame.mouse.set_visible(False)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.KEYUP:
            if event.key in (278, 270, 280, 276, 281, 275):
                client.send_keypress(event.key)
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            elif event.key in (13,32):
                client.toggle_notes()
            elif event.key == 288:
                client.increase_font()
            elif event.key == 289:
                client.decrease_font()
            else:
                print 'Key', event.key

        elif event.type == pygame.MOUSEMOTION:
            pygame.mouse.set_visible(True)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 1000)
        elif event.type == EVENT_HIDEMOUSE:
            pygame.mouse.set_visible(False)
            pygame.time.set_timer(EVENT_HIDEMOUSE, 0)
        else:
            pass
            #print event

if __name__ == '__main__':
    run()
