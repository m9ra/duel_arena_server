from threading import Thread

from configuration import MOVE_TIMEOUT, BOARD_SIZE, WIN_LENGTH
from game.board import Board


class Room():
    def __init__(self, arena, player1, player2):
        if player1.username == player2.username:
            raise ValueError("Cannot pair player against itself")

        self._arena = arena

        self._player1 = player1
        self._player2 = player2

        print(f"new room for {self._player1.username} and {self._player2.username}")

    @property
    def player1(self):
        return self._player1

    @property
    def player2(self):
        return self._player2

    def run_game(self):
        Thread(target=self._run_game, daemon=True).start()

    def _run_game(self):
        self._play_board(self._player1, self._player2)
        self._play_board(self._player2, self._player1)
        self._arena.room_ends(self)

    def _play_board(self, player1, player2):
        board = Board(BOARD_SIZE, WIN_LENGTH)
        self._arena.report_board_started(board, player1, player2)
        while not board.is_game_over:
            self._play_turn(player1, board)
            self._play_turn(player2, board)

        self._arena.report_board_finished(board)

    def _play_turn(self, player, board):
        if board.is_game_over:
            return

        other_player = self._other(player)

        x, y = player.get_move(board, MOVE_TIMEOUT)
        if not board.make_move(x, y):
            # invalid move or disconnection
            self._arena.report_invalid_move(player, x, y, board)
            self._arena.report_win(other_player, player, board)
            return

        self._arena.report_move(board)

        if board.is_win:
            self._arena.report_win(player, other_player, board)

    def _other(self, player):
        if player != self._player1 and player != self._player2:
            raise ValueError("Invalid player requested")

        if player == self._player1:
            return self._player2

        return self._player1
