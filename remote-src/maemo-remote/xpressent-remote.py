#! /usr/bin/env python

# Copyright 2009, Alvaro J. Iradier
#
# This file is part of xPressent (Maemo Remote).
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
import threading
import cStringIO
import socket
import os
import traceback
import base64
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

EVENT_HIDEMOUSE = pygame.USEREVENT + 1

LEFT_ARROW_B64 = \
"""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
"""

RIGHT_ARROW_B64 = \
"""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
NDQ0fI5ffWWI6QWMRgMAAAAASUVORK5CYII=
"""

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
        
        f = cStringIO.StringIO(base64.b64decode(LEFT_ARROW_B64))
        self.left_arrow = pygame.image.load(f, 'img.png')
        f.close()
        f = cStringIO.StringIO(base64.b64decode(RIGHT_ARROW_B64))
        self.right_arrow = pygame.image.load(f, 'img.png')
        f.close()

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
            
        self.screen.blit(self.left_arrow, (0,size[1]-self.left_arrow.get_size()[1]))
        self.screen.blit(self.right_arrow, (
            size[0] - self.right_arrow.get_size()[0],
            size[1]-self.right_arrow.get_size()[1]))
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
                self.font_size = self.screen.get_size()[1] / 12
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

    def prev_slide(self):
        self.send_keypress(280)

    def next_slide(self):
        self.send_keypress(281)
        
    def process_mouse_button(self, pos, button):
        if button == 1:
            screen_size = self.screen.get_size()
            if pos[0] < self.left_arrow.get_size()[0] \
                and pos[1] > screen_size[1] - self.left_arrow.get_size()[1]:
                self.prev_slide()
                return True
            elif pos[0] > screen_size[0] - self.right_arrow.get_size()[0] \
                and pos[1] > screen_size[1] - self.right_arrow.get_size()[1]:
                self.next_slide()
                return True

    def send_keypress(self, keycode):
        self.send(pack("!iii", PKT_KEYPRESS, 4, keycode))

    def run(self):

        size = self.screen.get_size()
        
        self.send(pack("!iiiii", PROT_VERSION, PKT_HELLO, 8, size[0], size[1]))
        
        version, = unpack("!i", self.recv(4))
        if version > PROT_VERSION:
            print "Unsupported server version: %d", version
            sys.exit(-1)
        
        hello, len = unpack("!ii", self.recv(8))
        if hello != PKT_HELLO or len != 0:
            print "Unexpected packet received"
            sys.exit(-1)

        while True:
            pkt_type, len = unpack("!ii", self.sock.recv(8))
            if pkt_type == PKT_CURRSLIDE and len > 4:
                page_number = unpack("!i", self.sock.recv(4))
                jpg_len, = unpack("!i", self.sock.recv(4))
                slide_jpg = self.read_bytes(jpg_len)
                notes_len, = unpack("!i", self.sock.recv(4))
                self.notes = str.decode(self.read_bytes(notes_len),'utf-8')
                f = cStringIO.StringIO()
                f.write(slide_jpg)
                f.seek(0)
                self.slide = pygame.image.load(f, 'img.jpg')
                self.slide.set_alpha(50)
                self.slide_alpha = pygame.Surface(self.slide.get_size())
                self.slide_alpha.blit(self.slide, (0,0))
                self.slide.set_alpha(None)
                f.close()
                self.notes_surface = None
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
    pygame.mouse.set_visible(True)

    mouse_dragging = False
    mouse_dragged = False
    mouse_last = (0,0)

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.KEYUP:
            if event.key in (275, 281):
                #Right, Next
                client.next_slide()
            elif event.key in (276, 280):
                #Left, Prev
                client.prev_slide()
            #elif event.key in (275, 276, 280, 281, 278, 279):
            #    #Left, Right, Prev, Next, Home, end
            #    
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_dragged = client.process_mouse_button(event.pos, event.button)
            if not mouse_dragged and event.button == 1:
                mouse_dragging = True
                mouse_last = event.pos
            else:
                mouse_dragging = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
            if not mouse_dragged:
                client.toggle_notes()
        elif event.type == pygame.MOUSEMOTION:
            mouse_dragged = True
            if mouse_dragging:
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
