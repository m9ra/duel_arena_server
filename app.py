from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap

from networking.server import Server
from score_record import ScoreRecord

server = Server()
server.listen(5226)

app = Flask(__name__)
app.secret_key = b'fer234\n\xec]/'
Bootstrap(app)


@app.route("/")
def index():
    scores = ScoreRecord.load_for(server.arena)
    return render_template("index.html", scores=scores)


@app.route("/results_table")
def results_table():
    scores = ScoreRecord.load_for(server.arena)
    return render_template("results_table.html", scores=scores)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5233)
