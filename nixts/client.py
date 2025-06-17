# This file is placed in the Public Domain.


"client"


import queue
import threading


from .errors  import later
from .fleet   import Fleet
from .handler import Handler
from .thread  import launch


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
            for tme in sorted(evt.result):
                self.say(evt.channel, evt.result[tme])

    def oput(self, evt):
        self.oqueue.put(evt)

    def output(self):
        while not self.ostop.is_set():
            try:
                evt = self.oqueue.get()
                if evt is None:
                    break
                self.display(evt)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            except Exception as ex:
                later(ex)
                _thread.interrupt_main()

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)

    #def start(self):
    #    super().start()
    #    launch(self.output)

    #def stop(self):
    #    super().stop()
    #    self.ostop.set()
    #    self.oqueue.put(None)


def __dir__():
    return (
        'Client',
    )
