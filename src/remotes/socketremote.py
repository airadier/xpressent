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
from remotebase import *
import socket

class SocketRemote(RemoteBase):

    def __init__ (self):
        RemoteBase.__init__(self)

    def initialize(self):
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind(("",48151))
            self.server_sock.listen(1)
            self.addr = self.server_sock.getsockname()[0]
            self.port = self.server_sock.getsockname()[1]
            return True
        except Exception, ex:
            print "Socket error:", ex
            return False

    def wait_connection(self):
        print "Waiting for socket connection on %s port %d" % (self.addr, self.port)
        client_sock, client_info = self.server_sock.accept()
        print "Got connection from ", client_info

        known_addresses = [x.strip().lower()
                           for x in config.get('remote:socket', 'known_addresses', '').split(',')]
        known_action = config.get('remote:socket', 'known_action', 'accept').lower()
        unknown_action = config.get('remote:socket', 'unknown_action', 'deny').lower()
        if client_info[0].lower() in known_addresses and known_action == 'deny':
                print "Rejecting known address"
                client_sock.close()
                return None
        if client_info[0].lower() not in known_addresses and unknown_action == 'deny':
                print "Rejecting unknown address"
                client_sock.close()
                return None

        return client_sock, client_info

    def shutdown(self):
        self.server_sock.close()


if config.getbool('remote:socket',  'enabled'):
    print "Enabling Socket remote"
    remote = SocketRemote()
    remote.start()
