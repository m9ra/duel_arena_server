from threading import RLock


class Board(object):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    _next_id = 1
    _L_id = RLock()

    def __init__(self, size, win_length, id=None, moves=None):
        if id is not None:
            self._id = id
        else:
            with Board._L_id:
                self._id = Board._next_id
                Board._next_id += 1

        self._win_length = win_length
        self._size = size
        self._is_game_over = False
        self._is_win = False

        self._fields = []
        self._moves = []
        for _ in range(size):
            self._fields.append([0] * size)

        if moves:
            for x, y in moves:
                self.try_make_move(x, y)

    @property
    def size(self):
        return self._size

    @property
    def win_length(self):
        return self._win_length

    @property
    def turn_index(self):
        return len(self._moves)

    @property
    def turn_color(self):
        return (self.turn_index % 2) * 2 - 1

    @property
    def is_game_over(self):
        return self._is_game_over or self._is_win or self.turn_index == self._size * self._size

    @property
    def is_win(self):
        return self._is_win

    def try_make_move(self, x, y):
        if self.is_game_over:
            raise ValueError("Can't make move when game is over.")

        if x < 0 or y < 0 or x >= self._size or y >= self._size:
            raise ValueError("Invalid coordinates given.")

        if self._fields[x][y] != 0:
            raise ValueError("Can't place move over another one.")

        self._fields[x][y] = self.turn_color
        self._is_win = self.check_win(x, y)
        self._moves.append((x, y))

    def make_move(self, x, y):
        try:
            self.try_make_move(x, y)

        except Exception:
            # invalid move detected - ends the game
            self._is_game_over = True
            return False

        return True

    def check_win(self, x, y):
        for direction in self.directions:
            segment = self.get_segment(x, y, direction, self._win_length)
            if self.longest_component(segment) >= self._win_length:
                return True

        return False

    def get_segment(self, x, y, direction, centered_halflength):
        curr_x = x - direction[0] * centered_halflength
        curr_y = y - direction[1] * centered_halflength

        segment = []
        for i in range(centered_halflength * 2 + 1):
            segment.append(self.get_color(curr_x, curr_y))
            curr_x += direction[0]
            curr_y += direction[1]

        return segment

    def get_color(self, x, y):
        if x < 0 or x >= self._size:
            return None

        if y < 0 or y >= self._size:
            return None

        return self._fields[x][y]

    def longest_component(self, segment):
        last_color = None
        current_length = 0
        lengths = [0]
        for color in segment + [None]:  # [None serves as a final delimiter]
            if color == last_color:
                current_length += 1
                continue

            if last_color:
                lengths.append(current_length)

            current_length = 1
            last_color = color

        return max(lengths)

    def to_str(self):
        result = ""
        for y in range(self._size):
            for x in range(self._size):
                color = self.get_color(x, y)
                if color == -1:
                    ch = 'X'
                elif color == 1:
                    ch = 'O'
                else:
                    ch = '*'

                result += ch

            result += '\n'

        return result

    @classmethod
    def deserialize(cls, json_data):
        board = Board(json_data["_size"], json_data["_win_length"], id=json_data["_id"], moves=json_data["_moves"])
        return board

    def serialize(self):
        return {
            "_id": self._id,
            "_size": self._size,
            "_win_length": self._win_length,
            "_moves": self._moves,
        }
