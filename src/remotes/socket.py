import config
from plugins import IPlugin
from events import *

if config.getbool('remote:socket',  'enabled'):
	print "Enabling remote"
