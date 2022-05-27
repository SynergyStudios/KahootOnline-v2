from .signal import Signal
from .server import Server
from .client import Client

from socket import gethostname, gethostbyname

def get_host():
    return gethostbyname(gethostname())
