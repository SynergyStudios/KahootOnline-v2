### The KahootOnline-v2 Project
### A Synergy Studios Collab

### Find on GitHub at: https://github.com/SynergyStudios/KahootOnline-v2

version = '1.0'
snapshot = '#a002'

from threading import Thread
from time import sleep

#from lib.utils import Printer
from lib.net import Server, Signal, get_host

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

class Player:

    """A player in the game, with a socket, addr, id
       and any other essentials."""

    def __init__(self, conn, addr, name, id = None):

        self.conn = conn
        self.addr = addr

        self.name = name
        self.id = id

        self.points = 0
        self.streak = 0

class Leaderboard:

    """Represents the leaderboard in the game."""

    def __init__(self):

        self.leaderboard = []


    def refresh(self):

        """Reorders the leaderboard."""

        self.leaderboard.sort(key = lambda x: x.count, reverse = True)

    def append(self, player, autosort = False):

        """Add a value to the leaderboard.
           If autosort is True, refreshes the leaderboard"""

        self.leaderboard.append(player)

        if autosort:
            self.refresh()

    def add_points(self, player, points, autosort = False):

        """Add points to a player in the leaderboard.
           If autosort is True, refreshes the leaderboard"""

        player.points += points

        if autosort:
            self.refresh()


    def print_leaderboard(self):

        """Prints out the leaderboard."""

        print('--- LEADERBOARD ---')

        for s in self.leaderboard:

            o = ordinal(self.leaderboard.index(s) + 1)

            print(f'{o}: Name: {s.name} | Points: {s.points} | Streak: {s.streak}')

    def return_position(self, player):

        """Returns the position of a player in the leaderboard."""

        for s in self.leaderboard:

            if s == player:
                return self.leaderboard.index(s) + 1
            

class SignalServer:

    """A custom server built around #signal."""

    def __init__(self):

        self.s = Server(63111)
        self.ip = self.s.IP

        self.st = '/*/'

        self.players = []

        self.question_queue = []
        self.question_queue_change = False

        self.state = None


    def get_player(conn):

        """Returns a player based on their connection."""

        pl = None

        for player in players:
            if player.conn == conn:
                pl = player

        return pl
        

    def setup_server(self, s):

        """Sets the server up as well as providing most of the
           game logic."""

        @s.Connected
        def handle_connection_on_server(conn):

            @conn.Signalled('/join') #/join
            def handle_join():

                """Handles a player joining and makes a Player() class to store their details."""

                name = signal.data['name']
                addr = signal.data['addr']
                
                self.players.append(Player(conn, addr, name))

                conn.send(Signal('/respondjoin', {'message': f'Successfully connected to uk.kahoot.server-{self.ip}',
                                                  'status': '200'}))

            @conn.Signalled('/version') #/version
            def check_version():

                """Checks the version of the client, and then either verifies it
                   or notifies and disconnects the client."""

                ver = signal.data['version']
                snap = signal.data['snapshot']

                if str(ver) != version:
                    conn.send(Signal('/wrongversion', {'error': f"You're running on an outdated version! Update to version {version} to play!",
                                                       'version_to_update': version}))

            @conn.Signalled('/result') #/result
            def mark_result():
                pass

            @conn.Signalled('/disconnect') #/disconnect
            def handle_disconnect():

                """Handles a disconnect from the client."""

                player = self.get_player(conn)

                if player:
                    self.players.remove(player)

                if conn.connection:
                    conn.disconnect()
                
    
        @s.Disconnected
        def unintended_disconnect():
            self.handle_disconnect()

    
    def start_server(self):

        """Starts the server after setting it up and connects
           everything together."""

        self.setup_server(self.s)
        self.start()

    def stop_server(self):

        """Stops the server."""

        self.s.stop()

class GameHandler:

    """Handles game logic and represents the running of
       the game."""

    def __init__(self):

        #self.server = SignalServer()
        #self.server_ip = self.server.ip

        #self.t = Thread(target = self.server.start_server, daemon = True)
        
        self.leaderboard = Leaderboard()
        #self.printer = Printer()

        #self.name = f'uk.kahoot.server-{self.server.ip}'

        self.questions =  []

        self.game_det = {'maxpoints': 1000,
                         'streak': False,
                         'questiontime': 20,
                         'questionpack': None,
                         'questionframe': 0.1}
        
        self.state = None

    def load_questions(self):

        """Loads questions in for the game."""

        if self.game_det['question_pack'] != None:
            self.game_det['question_pack'].add_pack(self.questions)

    def run_question(self, question):

        """Runs a question and sends it to the players."""

        pass

    def assign_points(self, player, question, time_taken):

        """Assigns points to a particular player."""

        pass


    def run_game(self):

        """The main loop that runs the game."""

        ### Broadcast start game
        self.state = 'Game'

        for q in self.questions:

            if len(self.server.players) > 0:

                self.server.question_queue = []
                print()
                
                self.run_question(q)
                print()

                # Run until time is up
                time_left = self.game_det['questiontime']
                time_board = []
                
                while time_left >= 0:

                    # Check for new response
                    if self.server.new_response:

                        new_answer = self.server.question_queue[-1:]
                        time_taken = round((self.qa_time - time_left), 3)

                        # Put time on board
                        time_board.append(time_taken)

                        self.server.new_response = False

                    # Everyone answered question
                    if len(self.server.question_queue) >= len(self.server.players):
                        break

                    sleep(self.game_det['questionframe'])
                    time_left = time_left(self.game_det['questionframe'])

                print()
                self.printer.print_border('single-border')

                # Print stats
                print(f'Client Answers: {self.server.question_queue}')
                print(f'Average Response Time: {sum(time_board) / len(time_board)} | Fastest Time: min(time_board)')

                # Assign answers
                for s in self.server.question_queue:
                    self.assign_points()

                # Print leaderboard
                self.leaderboard.refresh()
                self.leaderboard.print_leaderboard()

                print()
                self.printer.print_border('single-border')

            else:
                self.end_game()

        self.end_game()
                

    def lobby(self):

        """The waiting lobby, where the server can see who is in and who isn't."""

        self.state = 'Lobby'

        print('- LOBBY -')
        self.printer.print_border('single-border')

        input('When you are ready for the game to start hit [ENTER]')

        print()
        self.run_game()

    def start(self):

        """Sets up the server."""

        print('- BOOT -')
        self.printer.print_border('double-border')

        sleep(0.1)
        print('> Loading questions...')
        self.load_questions()

        sleep(0.5)
        print('> Starting connection...')
        self.t.start()

        sleep(0.1)
        print('> Setting up lobby...')
        print()
        

g = GameHandler()
#g.start()
