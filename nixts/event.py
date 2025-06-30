# This file is placed in the Public Domain.


"event"


import threading
import time


from .object import Object


class Event(Object):

    def __init__(self):
        Object.__init__(self)
        self._ready  = threading.Event()
        self._thr    = None
        self.channel = ""
        self.ctime   = time.time()
        self.orig    = ""
        self.rest    = ""
        self.result  = {}
        self.type    = "event"
        self.txt     = ""

    def done(self):
        self.reply("ok")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        if self._thr:
            self._thr.join()
        self._ready.wait(timeout)


def __dir__():
    return (
        'Event',
    )
