from socket import gethostbyname, gethostname
import socket
import ssl

# from .secure_connection import SecureConnection
from typing import List

from .connection import Connection as SecureConnection, Connection
from .parallel import Parallel
from .event import Event


class Server:
    BACKLOG = 7

    def __init__(self, port):
        self.IP = gethostbyname(gethostname())
        self.Port = port

        self.Connected = Event()
        self.Disconnected = Event()
        self.Stopped = Event()
        self.Started = Event()

        # self._context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # self._socket = self._context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections: List[Connection] = []

        self._event_loop = Parallel(self._loop)

        self.running = True

    def send_to_all(self, signal):
        for conn in self._connections:
            conn.send(signal)

    def start(self):
        self._socket.bind((self.IP, self.Port))
        self._socket.listen()

        self._event_loop.start()

    def stop(self):
        self.running = False

        for conn in self._connections:
            if conn.connected is True:
                conn.disconnect()

        self._event_loop.cancel()

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def _loop(self):
        while self.running is True:
            try:
                sock, info = self._socket.accept()

                connection = SecureConnection(sock)
                connection.listen()
                self._connections.append(connection)

                connection.Disconnected.connect(lambda: self.Disconnected.fire(connection))

                self.Connected.fire(connection)

            except ConnectionResetError as e:
                continue
