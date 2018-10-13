import datetime
import json
import sys

from flask import Flask, render_template, request, make_response
from flask_bootstrap import Bootstrap

from networking import websocket
from networking.server import Server
from score_record import ScoreRecord

if len(sys.argv) != 5:
    raise ValueError("Needs 4 arguments. arena_name, arena_port, http_port, weboscket_port");

arena_name = str(sys.argv[1])
arena_port = int(sys.argv[2])
http_port = int(sys.argv[3])
websocket_port = int(sys.argv[4])

server = Server(arena_name)
server.listen(arena_port)

app = Flask(__name__)
app.secret_key = b'fer234\n\xec]/'
Bootstrap(app)


@app.route("/board/<int:id>")
def board(id):
    board = server.arena.get_board(id)
    return render_template("board.html", b=board)


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
    return render_template("index.html", scores=scores, arena=server.arena.name, port=arena_port,
                           websocket_port=websocket_port)


@app.template_filter('ctime')
def timectime(s):
    if not s:
        return None

    return datetime.datetime.fromtimestamp(s).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    websocket.run_listener(websocket_port)
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=http_port)
