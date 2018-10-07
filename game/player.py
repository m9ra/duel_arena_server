import datetime
import queue
import random
import time
import traceback
from queue import Queue
from threading import Thread, RLock

from networking.socket_client import SocketClient


class Player(SocketClient):
    def __init__(self, socket):
        super().__init__(socket)
        self._arena = None
        self._moves = Queue()

    @property
    def username(self):
        return self._username

    def initialize(self, arena):
        try:
            self._arena = arena
            player_config = self.read_next_json()
            print(f"player: {player_config}")

            self._username = player_config["username"]
            self.send_json({"status": "ok"})
            arena.register_player(self)

            Thread(target=self._read_events, daemon=True).start()

        except Exception:
            print("Invalid player config.")
            traceback.print_exc()

    def _read_events(self):
        while self.is_connected:
            json = self.read_next_json()
            if json is None:
                break

            try:
                event_name = json["event"]
                if event_name == "make_move":
                    self._moves.put(json)
                elif event_name == "find_opponent":
                    self._arena.find_opponent_for(self)
                else:
                    raise NotImplementedError("Unknown event %s" % json)

            except Exception:
                traceback.print_exc()

    def get_move(self, board, timeout):
        move_id = f"{datetime.datetime.now().timestamp()}-{random.randint(0,100000)}"
        self.send_json({"event": "get_move", "id": move_id, "board": board.to_json()})

        start = time.time()

        while self.is_connected:
            # read data until timeout passes or move comes in
            elapsed_time = time.time() - start
            remaining_time = timeout - elapsed_time
            if remaining_time <= 0:
                break

            try:
                move = self._moves.get(timeout=remaining_time)
            except queue.Empty:
                # timeout
                break

            try:
                if move["id"] != move_id:
                    # probably an old move (that timeouted previously)
                    continue

                return (int(move["x"]), int(move["y"]))

            except Exception:
                print("Invalid move detected: %s" % move)
                traceback.print_exc()

        return (None, None)
