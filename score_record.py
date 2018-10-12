class ScoreRecord(object):
    def __init__(self, username, rating, wins, total_games, invalid_moves, total_seconds, is_online):
        self._username = username
        self._rating = rating
        self._wins = wins
        self._total_games = total_games
        self._invalid_moves = invalid_moves
        self._total_seconds = total_seconds
        self._is_online = is_online

    @classmethod
    def load_for(cls, arena):
        players, online_info = arena.load_players()
        records = []
        for player in players:
            records.append(
                ScoreRecord(player.get("_id"),
                            player.get("rating"),
                            player.get("wins"),
                            player.get("total_games"),
                            player.get("invalid_moves"),
                            player.get("total_seconds"),
                            is_online=online_info.get(player.get("_id"), False)
                            )
            )

        records.sort(key=lambda x: x.wins, reverse=True)
        return records

    @property
    def is_online(self):
        return self._is_online

    @property
    def username(self):
        return self._username

    @property
    def rating(self):
        return self._rating

    @property
    def wins(self):
        return self._wins

    @property
    def total_games(self):
        return self._total_games

    @property
    def invalid_moves(self):
        return self._invalid_moves

    @property
    def total_time(self):
        minutes = int(self._total_seconds / 60)
        hours = int(1.0 * self._total_seconds / 60 / 60)

        if not minutes and not hours:
            return f"{int(self._total_seconds):02d}s"

        if not hours:
            return f"{minutes}m{int(self._total_seconds) % 60:02d}"

        return f"{hours}h{minutes % 60:02d}"
