class CallbackEvent(object):
    def __init__(self, callback, *args):
        self._callback = callback
        self._args = args

    def run(self):
        self._callback(*self._args)
