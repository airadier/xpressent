#! /usr/bin/env python

import pygame
import sys
import threading
import cStringIO
import socket
import os
import traceback
from struct import pack, unpack
from pygame.locals import *
from pygame.event import Event
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

EVENT_HIDEMOUSE = pygame.USEREVENT + 1

class Screen(object):

    def __init__(self, fullscreen, size=(800,480)):
        self.size = size
        self.fullscreen = fullscreen
        self.surface = None

    def set_videomode(self):

        if not self.fullscreen:
            self.surface = pygame.display.set_mode(self.size)
        else:
            self.surface = pygame.display.set_mode(
                pygame.display.list_modes()[0],
                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)

    def get_size(self):
        return self.surface.get_width(), self.surface.get_height()

    def blit(self, source, position):
        self.surface.blit(source, position)

    def flip(self):
        pygame.display.flip()

    def clear(self):
        self.surface.fill((0,0,0))

class BaseClient(threading.Thread):

    def __init__(self, args, screen):
        threading.Thread.__init__(self)
        self.daemon = True
        self.screen = screen
        self.slide = None
        self.slide_alpha = None
        self.show_notes = False
        self.font = None
        self.font_size = None
        self.args = args
        self.notes = ""
        self.notes_surface = None
        self.notes_offset = 0

    def repaint_slide(self):
        if self.show_notes:
            slide = self.slide_alpha
        else:
            slide = self.slide

        self.screen.clear()
        size = self.screen.get_size()
        slide_size = slide.get_size()
        self.screen.blit(slide,(
                                (size[0]-slide_size[0])/2,
                                (size[1]-slide_size[1])/2))

        if self.show_notes: self.paint_notes()
        self.screen.flip()

    def get_lines(self, font, text, maxwidth):
        lines = []
        for line in text.split('\n'):
            current_line = ""
            for word in line.split(' '):
                for x in range(len(word)):
                    if font.size(current_line + ' ' + word[:x+1])[0] > maxwidth:
                        lines.append(current_line)
                        current_line = ""
                        break
                current_line = current_line + ' ' + word
            lines.append(current_line)
        return lines


    def paint_notes(self):
        screen_size = self.screen.get_size()
        margin_x = self.screen.get_size()[0]/50
        margin_y = self.screen.get_size()[1]/50
        if not self.notes_surface:
            if self.font_size == None:
                self.font_size = self.screen.get_size()[1] / 15
            font = pygame.font.SysFont("Helvetica, Sans, Arial", size=self.font_size)
            line_height = font.get_linesize()

            lines = self.get_lines(font, self.notes, screen_size[0] - (2*margin_x))
            self.notes_surface = pygame.Surface(
                (screen_size[0] - (2*margin_x),line_height*len(lines)),
                flags=pygame.HWSURFACE)
            self.notes_surface.set_colorkey((0,0,0), pygame.RLEACCEL)

            y  = 0
            for line in lines:
                line_surf = font.render(line, True, (255,255,255))
                self.notes_surface.blit(line_surf, (0,y))
                y = y + font.get_linesize()

        self.screen.blit(self.notes_surface,(margin_x,margin_y + self.notes_offset))

    def toggle_notes(self):
        self.show_notes = not self.show_notes
        self.repaint_slide()

    def read_bytes(self, length):
        read = ""
        while len(read) < length:
            read = read + self.recv(length - len(read))
        return read

    def decrease_font(self):
        if not self.show_notes: return
        self.font_size = self.font_size - 5
        if self.font_size < 5: self.font_size = 5
        self.notes_surface = None
        self.repaint_slide()

    def increase_font(self):
        if not self.show_notes: return
        self.font_size = self.font_size + 5
        self.notes_surface = None
        self.repaint_slide()

    def scroll(self, rel):
        if not self.show_notes: return
        if not self.notes_surface: return

        self.notes_offset = self.notes_offset + rel[1]
        if self.notes_offset > 0:
            self.notes_offset = 0
        elif self.notes_offset < 0 - self.notes_surface.get_height():
            self.notes_offset = 0 - self.notes_surface.get_height()

        self.repaint_slide()

    def quit(self):
        pygame.event.post(Event(pygame.QUIT))

    def send_keypress(self, keycode):
        self.send(pack("!ii", PKT_KEYPRESS, keycode))

    def run(self):

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
                self.notes_surface = None
                self.repaint_slide()
            elif pkt_type == PKT_CURRSLIDE:
                slide_len, page_number = unpack("!ii", self.sock.recv(8))
                slide_jpg = self.read_bytes(slide_len)
                f = cStringIO.StringIO()
                f.write(slide_jpg)
                f.seek(0)
                self.slide = pygame.image.load(f, 'img.jpg')
                self.slide.set_alpha(30)
                self.slide_alpha = pygame.Surface(self.slide.get_size())
                self.slide_alpha.blit(self.slide, (0,0))
                self.slide.set_alpha(None)
                f.close()
                self.notes = ""
                self.notes_offset = 0
                self.repaint_slide()

    def connect(self):
        raise NotImplementedError

    def recv(self, size):
        raise NotImplementedError

    def send(self, data):
        raise NotImplementedError

class BluetoothClient(BaseClient):
    def connect(self):

        if len(self.args) <1:
            print "No address specified, searching in all nearby devices..."
            addr = None
        else:
            addr = self.args[0]
            print "Searching Xpressent service in addr %s..." % addr

        service_matches = find_service(uuid = UUID, address = addr)
        if len(service_matches) == 0:
            print "Xpressent service not found"
            return False

        first_match = service_matches[0]
        print "Connecting to %s at %s" % (
            first_match['name'],
            first_match['host'])

        self.sock = BluetoothSocket(RFCOMM)
        self.sock.connect((first_match['host'], first_match['port']))

        return True

    def recv(self, size):
        return self.sock.recv(size)

    def send(self, data):
        return self.sock.send(data)

class SocketClient(BaseClient):

    def connect(self):
        addr = self.args[0].split(':')
        if len(addr) > 1:
            host = addr[0]
            port = int(addr[1])
        else:
            host = addr[0]
            port = 48151

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))

        return True

    def recv(self, size):
        return self.sock.recv(size)

    def send(self, data):
        return self.sock.send(data)

def run():

    pygame.init()

    if len(sys.argv) > 1 and sys.argv[1].lower() == '-f':
        fullscreen = True
        del sys.argv[1]
    else:
        fullscreen = False

    screen = Screen(fullscreen)
    connect = False

    try:
        if len(sys.argv) == 3 and sys.argv[1].lower() == '-s':
            client = SocketClient(sys.argv[2:], screen)
            connect = client.connect()
        elif len(sys.argv) in (2,3) and sys.argv[1].lower() == '-b':
            client = BluetoothClient(sys.argv[2:], screen)
            connect = client.connect()
        else:
            print "Usage: %s [-f] (-b [btaddr] | -s host:port)" % (os.path.basename(sys.argv[0]),)
            print
    except:
        traceback.print_exc()

    if not connect: sys.exit(-1)

    screen.set_videomode()
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
            if event.key in (275, 276, 280, 281, 278, 279):
                #Left, Right, Prev, Next, Home, end
                client.send_keypress(event.key)
            elif event.key == 27:
                #Escape key, exit
                sys.exit(0)
            elif event.key in (13,32):
                #Space or enter
                client.toggle_notes()
            elif event.key in (273, 288,):
                #Up, zoom in
                client.increase_font()
            elif event.key in (274, 289):
                #Down, zoom out
                client.decrease_font()
            else:
                print 'Key', event.key
        elif event.type == pygame.MOUSEMOTION:
            motions = [event]
            motions.extend(pygame.event.get(pygame.MOUSEMOTION))
            total_rel = (0,0)
            for motion_event in motions:
                if event.buttons[0]:
                    total_rel = (total_rel[0] + event.rel[0],
                                 total_rel[1] + event.rel[1])
            client.scroll(total_rel)
            #pygame.mouse.set_visible(True)
            #pygame.time.set_timer(EVENT_HIDEMOUSE, 1000)
        #elif event.type == EVENT_HIDEMOUSE:
            #pygame.mouse.set_visible(False)
            #pygame.time.set_timer(EVENT_HIDEMOUSE, 0)
        else:
            pass
            #print event

if __name__ == '__main__':
    run()