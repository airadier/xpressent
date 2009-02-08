import config
import pygame
from struct import pack, unpack
from bluetooth import *
from pygame.event import Event
from threading import Thread
from plugins.IPlugin import *

UUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41"

PROT_VERSION = 1
PKT_HELLO = 0
PKT_KEYPRESS = 1

class BluetoothRemote(Thread):   

    def __init__ (self):
        Thread.__init__(self)
        self.daemon = True
        self._socket = None
        self.clients = []
   
    def slide_change(self, slidemanager, page_number, notes):
        print "Slide changed"
        print notes
        for client in self.clients:
            client.send(notes)
   
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

                self.clients.append(client_sock)
                while True:
                    data = client_sock.recv(1024)                  
                    print "received [%s]" % data
                    pygame.event.post(Event(pygame.KEYUP, key=281, mod=None))
            except IOError:
                pass
    
            print "BT Client Disconnected"

            self.clients.remove(client_sock)
            client_sock.close()

        server_sock.close()

if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling bluetooth remote"
    remote = BluetoothRemote()
    remote.start()
