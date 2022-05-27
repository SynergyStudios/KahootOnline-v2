from json import dumps, loads
from base64 import b64encode, b64decode


class Signal:
    ENCODING = "utf-8"

    def __init__(self, path="*", data=None):
        self.path = path
        self.data = data or {}

    @staticmethod
    def decode(encoded: bytes):
        decoded = loads(b64decode(encoded).decode(Signal.ENCODING))
        path = decoded["path"]
        data = decoded["data"]

        return Signal(path, data)

    def encoded(self):
        return bytes(self)

    def __bytes__(self):
        return b64encode(dumps({
            "path": self.path,
            "data": self.data
        }).encode(Signal.ENCODING))
