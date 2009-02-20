# Copyright 2009, Alvaro J. Iradier
# This file is part of xPressent.
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

import config
from bluetooth import *
from plugins.IPlugin import *
from remotebase import *

UUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41"

class BluetoothRemote(RemoteBase):

    def __init__ (self):
        RemoteBase.__init__(self)
        
    def initialize(self):
        try:
            self.server_sock = BluetoothSocket( RFCOMM )
            self.server_sock.bind(("",PORT_ANY))
            self.server_sock.listen(1)

            self.addr = self.server_sock.getsockname()[0]
            self.port = self.server_sock.getsockname()[1]

            advertise_service( self.server_sock, "XPressent Remote Server",
                              service_id = UUID,
                              service_classes = [ UUID, SERIAL_PORT_CLASS ],
                              profiles = [ SERIAL_PORT_PROFILE ] )
            return True
        except Exception, ex:
            print "BT Error:", ex
            return False
        
    def wait_connection(self):
        print "Waiting for Bluetooth RFCOMM connection on %s channel %d" % (self.addr, self.port)
        client_sock, client_info = self.server_sock.accept()
        print "Got connection from ", client_info
        return client_sock, client_info

        
    def shutdown(self):
        self.server_sock.close()

if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling Bluetooth remote"
    remote = BluetoothRemote()
    remote.start()
