# This file is placed in the Public Domain.


"event handler"


import queue
import threading
import time
import _thread


from .object import Object
from .thread import later, launch, name


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


class Handler:

    def __init__(self):
        self.cblock  = _thread.allocate_lock()
        self.cbs     = {}
        self.queue   = queue.Queue()
        self.ready   = threading.Event()
        self.stopped = threading.Event()
        self.threshold = 50

    def callback(self, evt):
        with self.cblock:
            func = self.cbs.get(evt.type, None)
            if not func:
                evt.ready()
                return
            if evt.txt:
                cmd = evt.txt.split(maxsplit=1)[0]
            else:
                cmd = name(func)
            evt._thr = launch(func, evt, name=cmd, daemon=True)

    def loop(self):
        while not self.stopped.is_set():
            try:
                evt = self.poll()
                if evt is None:
                    break
                evt.orig = repr(self)
                self.callback(evt)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            except Exception as ex:
                later(ex)
                _thread.interrupt_main()
        self.ready.set()

    def poll(self):
        return self.queue.get()

    def put(self, evt):
        self.queue.put(evt)

    def register(self, typ, cbs):
        self.cbs[typ] = cbs

    def start(self):
        self.stopped.clear()
        self.ready.clear()
        launch(self.loop)

    def stop(self):
        self.stopped.set()
        self.queue.put(None)

    def wait(self):
        self.ready.wait()


def __dir__():
    return (
        'Event',
        'Handler'
    )
