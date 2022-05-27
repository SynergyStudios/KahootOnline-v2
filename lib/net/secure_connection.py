import socket
import ssl

from .connection import Connection


class SecureConnection(Connection):
    def __init__(self, sock: socket.socket):
        super().__init__(sock)

        self._context = ssl.SSLContext()
        self._socket = self._context.wrap_socket(sock)

    def send(self, data):
        pass
