import config
from bluetooth import *
from plugins.IPlugin import *
from remotebase import *

UUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41"

class BluetoothRemote(RemoteBase):

    def __init__ (self):
        RemoteBase.__init__(self)
        
    def send(self, client, data):
        client.send(data)

    def recv(self, client, bytes):
        read = ""
        while len(read) < bytes:
            read = read + client.recv(bytes)
        
        return read

    def close(self, client):
        client.close()
        
    def initialize(self):
        try:
            self.server_sock = BluetoothSocket( RFCOMM )
            self.server_sock.bind(("",PORT_ANY))
            self.server_sock.listen(1)

            print "sockname", self.server_sock.getsockname()
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
        print "Waiting for connection on RFCOMM channel %d" % self.port
        client_sock, client_info = self.server_sock.accept()
        print "Got connection from ", client_info
        return client_sock, client_info

        
    def shutdown(self):
        self.server_sock.close()

if config.getbool('remote:bluetooth',  'enabled'):
    print "Enabling bluetooth remote"
    remote = BluetoothRemote()
    remote.start()
