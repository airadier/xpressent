import config
import pygame
import Image
import cStringIO
from struct import pack, unpack
from bluetooth import *
from pygame.event import Event
from threading import Thread
from plugins.IPlugin import *

UUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41"

PROT_VERSION = 1
PKT_HELLO = 0
PKT_KEYPRESS = 1
PKT_CURRSLIDE = 2
PKT_NEXTSLIDE = 3
PKT_PREVSLIDE = 4
PKT_NOTES = 5


class BluetoothRemote(Thread):

    def __init__ (self):
        Thread.__init__(self)
        self.daemon = True
        self._socket = None
        self.clients = []
        self.remote_size = (640, 480)
        self.current_slide = None
        self.current_notes = None
        self.slidemanager = None
        self.page_number = None

    def slide_change(self, slidemanager, page_number, slide, notes, client=None):

        if not slidemanager: return

        imgstr = pygame.image.tostring(slide, 'RGB')
        pil_image = Image.fromstring('RGB', slide.get_size(), imgstr)
        f = cStringIO.StringIO()
        pil_image.save(f, 'PNG')
        slide_png = f.getvalue()
        f.close()

        #Send current slide to all clients
        for client in [client] if client else self.clients:
            print "Sending %d bytes of slide" % len(slide_png)
            try:
                client.send(pack("!iii", PKT_CURRSLIDE, len(slide_png), page_number))
                client.send(slide_png)
            except:
                pass

        #Send notes to all clients
        for client in [client] if client else self.clients:
            try:
                client.send(pack("!ii", PKT_NOTES, len(notes)))
                client.send(notes)
            except:
                pass
        
        self.slidemanager = slidemanager
        self.current_slide = slide_png
        self.current_notes = notes
        self.page_number = page_number

    def run(self):

        register_event_listener(EVENT_SLIDECHANGE, self.slide_change)
        server_sock = BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)


        print "sockname", server_sock.getsockname()
        port = server_sock.getsockname()[1]

        advertise_service( server_sock, "XPressent Remote Server",
                          service_id = UUID,
                          service_classes = [ UUID, SERIAL_PORT_CLASS ],
                          profiles = [ SERIAL_PORT_PROFILE ] )

        while True:
            print "Waiting for connection on RFCOMM channel %d" % port

            client_sock, client_info = server_sock.accept()
            print "Got connection from ", client_info

            try:
                client_sock.send(pack("!ii", PROT_VERSION, PKT_HELLO))
                version, = unpack("!i", client_sock.recv(4))
                if version > PROT_VERSION:
                    print "Unsupported client version: %d", version
                    raise IOError
                if unpack("!i", client_sock.recv(4))[0] != PKT_HELLO:
                    print "Unexpected message received"
                    raise IOError

                self.client_size = unpack("!ii", client_sock.recv(8))
                self.clients.append(client_sock)
                
                #Send current slide to client
                self.slide_change(self.slidemanager, self.page_number, self.current_slide, self.current_notes, client = client_sock)

                while True:
                    pkt_type, = unpack("!i", client_sock.recv(4))

                    if pkt_type == PKT_KEYPRESS:
                        key, = unpack("!i", client_sock.recv(4))
                        pygame.event.post(Event(pygame.KEYUP, key=key, mod=None))

            except IOError:
                pass
            except Exception:
                print "BT Error"

            print "BT Client Disconnected"

            self.clients.remove(client_sock)
            client_sock.close()

        server_sock.close()

if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling bluetooth remote"
    remote = BluetoothRemote()
    remote.start()
