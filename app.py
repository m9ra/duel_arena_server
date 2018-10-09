import datetime
import time

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from networking.server import Server
from score_record import ScoreRecord

server = Server()
server.listen(5226)

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
    return render_template("index.html", scores=scores)


@app.template_filter('ctime')
def timectime(s):
    if not s:
        return None

    return datetime.datetime.fromtimestamp(s).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5233)
