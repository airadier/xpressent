import config
import pygame
from bluetooth import *
from pygame.event import Event
from threading import Thread
from plugins import IPlugin

class BluetoothRemote(Thread):   
   
   def __init__ (self):
    Thread.__init__(self)
    self.daemon = True
    self._socket = None
   
   def run(self):

        server_sock = BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)
        
        print "sockname", server_sock.getsockname()
        port = server_sock.getsockname()[1]

        uuid = "829abc54-a67d-0e10-ba67-00bc59a5ce41"
        advertise_service( server_sock, "XPressent Remote Server",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ] )

        print "Waiting for connection on RFCOMM channel %d" % port

        client_sock, client_info = server_sock.accept()
        print "Accepted connection from ", client_info

        try:
            while True:
                data = client_sock.recv(1024)
                print "received [%s]" % data
                pygame.event.post(Event(pygame.KEYUP, key=281, mod=None))
        except IOError:
            pass

        print "disconnected"

        client_sock.close()
        server_sock.close()


if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling bluetooth remote"
    remote = BluetoothRemote()
    remote.start()
