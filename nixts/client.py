# This file is placed in the Public Domain.


"client"


import queue
import threading
import _thread


from .fleet   import Fleet
from .handler import Handler
from .thread  import later, launch


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.olock  = threading.RLock()
        self.oqueue = queue.Queue()
        self.ostop  = threading.Event()
        Fleet.add(self)

    def announce(self, txt):
        pass

    def display(self, evt):
        with self.olock:
            if self.ostop.is_set():
                return
            for tme in sorted(evt.result):
                self.dosay(evt.channel, evt.result[tme])
            evt.ready()

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def oput(self, evt):
        self.oqueue.put(evt)

    def output(self):
        while not self.ostop.is_set():
            try:
                evt = self.oqueue.get()
                if evt is None:
                    break
                self.display(evt)
                self.oqueue.task_done()
                evt.ready()
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            except Exception as ex:
                later(ex)
                _thread.interrupt_main()

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        launch(self.output)
        super().start()

    def stop(self):
        self.ostop.set()
        self.oqueue.put(None)
        super().stop()


def __dir__():
    return (
        'Client',
    )
