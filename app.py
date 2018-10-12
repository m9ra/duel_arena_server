import datetime
import json
import sys

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from networking.server import Server
from score_record import ScoreRecord

if len(sys.argv) != 4:
    raise ValueError("Needs 3 arguments. http_port, arena_port, arena_name");

arena_name = str(sys.argv[1])
arena_port = int(sys.argv[2])
http_port = int(sys.argv[3])

server = Server(arena_name)
server.listen(arena_port)

app = Flask(__name__)
app.secret_key = b'fer234\n\xec]/'
Bootstrap(app)


@app.route("/board/<int:id>")
def board(id):
    board = server.arena.get_board(id)
    return render_template("board.html", b=board)


@app.route("/live_board")
def live_board():
    id = request.args.get("id")
    move = request.args.get("move")

    return json.dumps(server.arena.get_live_board(id, move, 5.0))


@app.route("/profile/<player>")
def profile(player):
    history, board_count = server.arena.get_history(player)
    rating = server.arena.get_rating(player)
    return render_template("profile.html", player=player, rating=rating, history=history, board_count=board_count)


@app.route("/history")
def history():
    history, board_count = server.arena.get_history()
    return render_template("profile.html", history=history, board_count=board_count)


@app.route("/results_table")
def results_table():
    scores = ScoreRecord.load_for(server.arena)
    return render_template("results_table.html", scores=scores)


@app.route("/")
def index():
    scores = ScoreRecord.load_for(server.arena)
    return render_template("index.html", scores=scores, arena=server.arena.name, port=arena_port)


@app.template_filter('ctime')
def timectime(s):
    if not s:
        return None

    return datetime.datetime.fromtimestamp(s).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=http_port)
