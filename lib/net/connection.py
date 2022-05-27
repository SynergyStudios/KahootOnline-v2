import socket

from .event import Event, ConditionalEvent
from .signal import Signal
from .parallel import Parallel


class Connection:
    TERMINATOR = b"\n"
    CHUNK_SIZE = 1024

    def __init__(self, sock: socket.socket):
        self.ip = sock.getpeername()
        self._socket = sock

        self.Signalled = ConditionalEvent(lambda signal: [signal.path], default="*")
        self.Disconnected = Event()

        self.connected = False
        self._event_loop = Parallel(self._listen)

    def listen(self):
        self.connected = True

        self._event_loop.start()

    def disconnect(self):
        self.send(Signal("/__disconnect"))
        self._close()

    def _close(self):
        self.connected = False
        self.Disconnected.fire()

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        self._event_loop.cancel()

    def _listen(self):
        while self.connected:
            stream = b""

            while Connection.TERMINATOR not in stream:
                stream += self._socket.recv(Connection.CHUNK_SIZE)

            packet = Signal.decode(stream.split(Connection.TERMINATOR)[0])

            if packet.path == "/__disconnect":
                self._close()

            else:
                self.Signalled.fire(packet)

    def send(self, data):
        encoded = bytes(data) + Connection.TERMINATOR

        size = len(encoded)
        current_chunks = 0
        while current_chunks < size:
            chunked_data = encoded[current_chunks:current_chunks + Connection.CHUNK_SIZE]
            self._socket.send(chunked_data)
            current_chunks += Connection.CHUNK_SIZE
