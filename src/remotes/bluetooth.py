import config
from threading import Thread
from plugins import IPlugin
import pygame
from pygame.event import Event
import time

if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling bluetooth remote"
    remote = BluetoothRemote()
    remote.start()


class BluetoothRemote(Thread):   
   
   def __init__ (self):
    Thread.__init__(self)
    self.setDaemon(True)
    self._socket = None
   
   def run(self):
       while True:
           time.sleep(3)
           print "Voy bluetooth"
           pygame.event.post(Event(pygame.KEYUP, key=281, mod=None))


