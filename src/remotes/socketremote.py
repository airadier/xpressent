import config
from remotebase import *
import socket

class SocketRemote(RemoteBase):
   
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
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind(("",48151))
            self.server_sock.listen(1)
            self.port = self.server_sock.getsockname()[1]
            return True
        except Exception, ex:
            print "Socket error:", ex
            return False

    def wait_connection(self):
        print "Waiting for connection on port %d" % self.port
        client_sock, client_info = self.server_sock.accept()
        print "Got connection from ", client_info
        return client_sock, client_info

    def shutdown(self):
        self.server_sock.close()


if config.getbool('remote:socket',  'enabled'):
    print "Enabling socket remote"
    remote = SocketRemote()
    remote.start()
