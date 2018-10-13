import asyncio
import json
from queue import Queue
from threading import Thread, RLock

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

_L_websockets = RLock()
_clients = []
_data_to_send = Queue()


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        with _L_websockets:
            _clients.append(self)

    def on_message(self, message):
        pass  # no incomming messages are expected

    def on_close(self):
        with _L_websockets:
            _clients.remove(self)

    def check_origin(self, origin):
        return True


def broadcast(data):
    _data_to_send.put(data)


def run_listener(websocket_port):
    def _run():
        asyncio.set_event_loop(asyncio.new_event_loop())
        application = tornado.web.Application([
            (r'/ws', WSHandler),
        ])

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(websocket_port)
        tornado.ioloop.IOLoop.instance().start()

    th = Thread(target=_run, daemon=True)
    th.start()

    sender = Thread(target=_sender, daemon=True)
    sender.start()


def _sender():
    while True:
        data = _data_to_send.get()
        if not data:
            continue

        json_data = json.dumps(data)
        with _L_websockets:
            for client in _clients:
                client.write_message(json_data)
