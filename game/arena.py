import random
import time
from threading import RLock

from pymongo import MongoClient

from configuration import PAIRING_TRIGGER_DELAY
from events import worker
from game.board import Board
from game.room import Room

_db_name = "arena"
_client = MongoClient()
_db = _client[_db_name]


class Arena(object):
    def __init__(self, name):
        self._collection = _db[name]
        # self._collection.players.delete_many({})
        # self._collection.boards.delete_many({})
        self._L_collection = RLock()
        self._name = name
        self._free_players = []
        self._playing_players = []
        self._players = {}
        self._rooms = []
        self._last_time_check = time.time()

        Board.initialize_id(self._get_highest_board_id())

        worker.set_timer(PAIRING_TRIGGER_DELAY, self._run_pairing)
        worker.set_timer(1.0, self._count_online_time)

    def load_players(self):
        with self._L_collection:
            return list(self._collection.players.find({}))

    def get_history(self, username=None):
        with self._L_collection:
            if username:
                query = {"$or": [{"player1": username}, {"player2": username}]}
            else:
                query = {}
            cursor = self._collection.boards.find(query)
            return list(cursor.sort("start_time", -1).limit(100)), cursor.count()

    def get_board(self, board_id):
        with self._L_collection:
            return self._collection.boards.find_one({"_id": board_id})

    def register_player(self, player):
        worker.execute(self._register_player, player)

    def find_opponent_for(self, player):
        worker.execute(self._find_opponent_for, player)

    def room_ends(self, room):
        worker.execute(self._room_ends, room)

    def report_invalid_move(self, player, x, y, board):
        worker.execute(self._report_invalid_move, player, x, y, board)

    def report_win(self, winner, looser, board):
        worker.execute(self._report_win, winner, looser, board)

    def report_board_started(self, board, player1, player2):
        rating1 = self.get_rating(player1)
        rating2 = self.get_rating(player2)

        worker.execute(self._report_board_started, board, player1, rating1, player2, rating2)

    def report_move(self, board):
        worker.execute(self._report_move, board, board.moves[-1])

    def report_board_finished(self, board):
        worker.execute(self._report_board_finished, board)

    def _get_highest_board_id(self):
        with self._L_collection:
            for board in self._collection.boards.find({}).sort("_id", -1).limit(1):
                return board["_id"]

        return 0

    def _report_board_started(self, board, player1, rating1, player2, rating2):
        with self._L_collection:
            self._collection.boards.insert({
                "_id": board.id,
                "player1": player1.username,
                "player2": player2.username,
                "rating1": rating1,
                "rating2": rating2,
                "start_time": time.time(),
                "end_time": None,
                "moves": []
            })

    def _report_move(self, board, move):
        with self._L_collection:
            self._collection.boards.update(
                {"_id": board.id},
                {"$push": {
                    "moves": move
                }}
            )

    def _report_board_finished(self, board):
        self._collection.boards.update(
            {"_id": board.id},
            {"$set": {
                "end_time": time.time()
            }}
        )

    def _report_invalid_move(self, player, x, y, board):
        player.send_json({"event": "invalid_move", "x": x, "y": y, "board": board.serialize()})
        with self._L_collection:
            self._collection.players.update({"_id": player.username}, {
                "$inc": {
                    "invalid_moves": 1,
                }
            }, upsert=True)

    def _report_win(self, winner, looser, board):
        winner.send_json({"event": "win", "board": board.serialize()})

        with self._L_collection:
            rating_winner = self.get_rating(winner)
            rating_looser = self.get_rating(looser)

            p1 = self._expected_win_probability(rating_winner, rating_looser)
            p2 = self._expected_win_probability(rating_looser, rating_winner)
            K = 30
            new_rating_winner = rating_winner + K * (1 - p1)
            new_rating_looser = rating_looser + K * (0 - p2)

            self._collection.players.update({"_id": winner.username}, {
                "$inc": {
                    "wins": 1,
                    "total_games": 1,
                },
                "$set": {
                    "rating": new_rating_winner
                }
            }, upsert=True)

        looser.send_json({"event": "lose", "board": board.serialize()})
        with self._L_collection:
            self._collection.players.update({"_id": looser.username}, {
                "$inc": {
                    "losses": 1,
                    "total_games": 1,
                },
                "$set": {
                    "rating": new_rating_looser
                }
            }, upsert=True)

        with self._L_collection:
            self._collection.boards.update({"_id": board.id}, {"$set": {"winner": winner.username}})

    def _register_player(self, player):
        if not player.is_connected:
            return

        old_player = self._players.get(player.username, None)
        if old_player:
            old_player.disconnect()

        self._players[player.username] = player

        with self._L_collection:
            self._ensure_default(player, "rating", 1200)
            self._ensure_default(player, "wins", 0)
            self._ensure_default(player, "invalid_moves", 0)
            self._ensure_default(player, "total_seconds", 0)
            self._ensure_default(player, "total_games", 0)

        self._report_player_is_free(player)

    def _ensure_default(self, player, field, value):
        with self._L_collection:
            if not self._collection.players.find_one({"_id": player.username}):
                self._collection.players.insert({"_id": player.username})

            self._collection.players.update({"_id": player.username, field: {"$exists": False}},
                                            {"$set": {field: value}})

    def _report_player_is_free(self, player):
        player.send_json({"event": "player_is_free"})

        if player in self._playing_players:
            self._playing_players.remove(player)

    def _find_opponent_for(self, player):
        if not player.is_connected:
            return

        if player not in self._free_players and player not in self._playing_players:
            self._free_players.append(player)

    def _room_ends(self, room):
        self._rooms.remove(room)
        self._report_player_is_free(room.player1)
        self._report_player_is_free(room.player2)

    def _count_online_time(self):
        current_time = time.time()
        extra_time = current_time - self._last_time_check
        self._last_time_check = current_time

        for player in self._players.values():
            if player.is_connected:
                with self._L_collection:
                    self._collection.players.update({"_id": player.username}, {
                        "$inc": {
                            "total_seconds": extra_time,
                        },
                    })

    def _run_pairing(self):
        self._remove_offline_free_players()

        players = list(self._free_players)
        random.shuffle(players)

        for i in range(int(len(players) / 2)):
            p1 = players[i * 2]
            p2 = players[i * 2 + 1]
            room = Room(self, p1, p2)

            self._free_players.remove(p1)
            self._free_players.remove(p2)

            self._playing_players.append(p1)
            self._playing_players.append(p2)

            p1.send_json({"event": "starting_game", "against": p2.username})
            p2.send_json({"event": "starting_game", "against": p1.username})

            self._rooms.append(room)
            room.run_game()

    def _remove_offline_free_players(self):
        for i in reversed(range(len(self._free_players))):
            if not self._free_players[i].is_connected:
                del self._free_players[i]

    def _expected_win_probability(self, rating1, rating2):
        return (1.0 / (1.0 + pow(10, ((rating2 - rating1) / 400))))

    def get_rating(self, player):
        with self._L_collection:
            if isinstance(player, str):
                username = player
            else:
                username = player.username

            return self._collection.players.find_one({"_id": username})["rating"]
