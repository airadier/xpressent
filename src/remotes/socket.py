import config
from threading import Thread
from plugins import IPlugin
from events import *
import time

if config.getbool('remote:socket',  'enabled'):
    print "Enabling remote"
    
class SocketRemote(Thread):   
   
   def __init__ (self):
    Thread.__init__(self)
    self.setDaemon(True)
    self._socket = None
   
   def run(self):
       while True:
           print "Voy"
           time.sleep(3)

remote = SocketRemote()
remote.start()