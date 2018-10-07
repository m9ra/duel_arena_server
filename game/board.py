from threading import RLock


class Board(object):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    _next_id = 1
    _L_id = RLock()

    def __init__(self, size, win_length):
        with Board._L_id:
            self._id = Board._next_id
            Board._next_id += 1

        self._win_length = win_length
        self._size = size
        self._is_game_over = False
        self._is_win = False
        self._turn_index = 0

        self._fields = []
        for _ in range(size):
            self._fields.append([0] * size)

    @property
    def is_game_over(self):
        return self._is_game_over or self._is_win or self._turn_index == self._size * self._size

    @property
    def is_win(self):
        return self._is_win

    @property
    def color_on_turn(self):
        return (self._turn_index % 2) * 2 - 1

    def try_make_move(self, x, y):
        if self.is_game_over:
            raise ValueError("Can't make move when game is over.")

        if x < 0 or y < 0 or x >= self._size or y >= self._size:
            raise ValueError("Invalid coordinates given.")

        if self._fields[x][y] != 0:
            raise ValueError("Can't place move over another one.")

        self._fields[x][y] = self.color_on_turn
        self._is_win = self.check_win(x, y)
        self._turn_index += 1

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

    def to_json(self):
        return {
            "_id": self._id,
            "_turn_index": self._turn_index,
            "_is_win": self._is_win,
            "_is_game_over": self._is_game_over,
            "_fields": self._fields,
            "_size": self._size,
            "_win_length": self._win_length
        }
