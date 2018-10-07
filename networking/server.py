import socket
from threading import Thread

from game.arena import Arena
from game.player import Player


class Server(object):

    @property
    def arena(self):
        return self._arena

    def __init__(self):
        self._arena = Arena("debug_arena")

    def listen(self, port):
        Thread(target=self._accept_clients, args=[port], daemon=True).start()

    def _accept_clients(self, port):
        listening_socket = self._prepare_listening_socket(port)

        while True:
            print("listening...")
            client_socket, addr = listening_socket.accept()
            Thread(target=self._accept_player, args=[client_socket, addr], daemon=True).start()

    def _accept_player(self, socket, addr):
        player = Player(socket)
        player.initialize(self._arena)

    def _prepare_listening_socket(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen()
        return s
