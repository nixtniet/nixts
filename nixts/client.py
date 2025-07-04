# This file is placed in the Public Domain.


"client"


import queue
import threading


from .engine import Engine
from .fleet  import Fleet
from .thread import launch


class Client(Engine):

    def __init__(self):
        Engine.__init__(self)
        self.olock  = threading.RLock()
        Fleet.add(self)

    def announce(self, txt):
        pass

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(event.channel, event.result[tme])
            event.ready()

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


"output"


class Output(Client):

    def __init__(self):
        Client.__init__(self)
        self.oqueue = queue.Queue()
        self.oready = threading.Event()
        self.ostop = threading.Event()

    def oput(self, event):
        self.oqueue.put(event)

    def output(self):
        while not self.ostop.is_set():
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()
        self.oready.set()

    def start(self):
        super().start()
        self.oready.clear()
        self.ostop.clear()
        launch(self.output)

    def stop(self):
        super().stop()
        self.ostop.set()
        self.oqueue.put(None)
        self.oready.wait()

    def wait(self):
        self.oqueue.join()
        super().wait()


"interface"


def __dir__():
    return (
        'Client',
        'Output'
    )
