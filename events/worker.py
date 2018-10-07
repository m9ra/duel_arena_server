import traceback
from queue import Queue
from threading import Thread
from time import sleep

from events.callback_event import CallbackEvent

_events = Queue()


def _process_events():
    while True:
        event = _events.get()
        try:
            event.run()
        except Exception:
            traceback.print_exc()


_worker = Thread(target=_process_events, daemon=True)
_worker.start()


def set_timer(interval, action):
    Thread(target=_run_timer, args=[interval, action], daemon=True).start()


def _run_timer(interval, action):
    while True:
        sleep(interval)
        execute(action)


def execute(callback, *args):
    _events.put(CallbackEvent(callback, *args))
