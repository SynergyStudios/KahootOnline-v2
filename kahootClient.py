### The KahootOnline-v2 Project
### A Synergy Studios Collab

### Find on GitHub at: https://github.com/SynergyStudios/KahootOnline-v2

version = '1.0'
snapshot = '#a002'

from threading import Thread
from time import sleep

from lib.utils import Printer
from lib.net import Client, Signal, get_host


class SignalClient:

    """A custom client built around #signal."""

    def __init__(self):

         self.c = Client(gethostname(), 63111)
         self.ip = self.c.IP
         
         self.st = '/*/'

         self.state = None

    def setup_client(self, c):

        """Sets up a client as well as providing most of the
           game logic."""

        @c.Connected
        def handle_connection_on_client(conn):

            @conn.Signalled('/respondjoin') #/respondjoin
            def handle_respondjoin():

                """Gets a repsonse after sending a /join command."""

                message = signal.data['name']
                status = signal.data['status']

                if status == '200':
                    print(message)

            @conn.Signalled('/wrongversion') #/wrongversion
            def wrong_version():
                pass


class GameHandler:

    """Handles game logic and represents the running of
       the game."""

    def __init__(self):

        #self.client = SignalClient()
        #self.ip = self.client.ip

        #self.t = Thread(target = self.server.start_server, daemon = True)

        #self.printer = Printer()

        #self.name = None

        self.state = None

        

g = GameHandler()
#g.start()
