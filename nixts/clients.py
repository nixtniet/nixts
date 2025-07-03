# This file is placed in the Public Domain.


"clients"


import queue
import threading
import _thread


from .handler import Handler
from .threads import later, launch


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.olock  = threading.RLock()
        Fleet.add(self)

    def announce(self, txt):
        pass

    def display(self, evt):
        with self.olock:
            for tme in sorted(evt.result):
                self.dosay(evt.channel, evt.result[tme])
            evt.ready()

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


"buffered"


class Buffered(Client):

    def __init__(self):
        Client.__init__(self)
        self.oqueue = queue.Queue()
        self.ostop  = threading.Event()

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
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            except Exception as ex:
                later(ex)
                _thread.interrupt_main()

    def start(self):
        launch(self.output)
        super().start()

    def stop(self):
        self.ostop.set()
        self.oqueue.put(None)
        super().stop()


"fleet"


class Fleet:

    clients = {}

    @staticmethod
    def add(clt):
        Fleet.clients[repr(clt)] = clt

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(txt):
        for clt in Fleet.all():
            clt.announce(txt)

    @staticmethod
    def dispatch(evt):
        clt = Fleet.get(evt.orig)
        clt.put(evt)

    @staticmethod
    def display(evt):
        clt = Fleet.get(evt.orig)
        clt.display(evt)

    @staticmethod
    def first():
        clt =  list(Fleet.all())
        res = None
        if clt:
            res = clt[0]
        return res

    @staticmethod
    def get(orig):
        return Fleet.clients.get(orig, None)

    @staticmethod
    def say(orig, channel, txt):
        clt = Fleet.get(orig)
        if clt:
            clt.say(channel, txt)

    @staticmethod
    def shutdown():
        for clt in Fleet.all():
            if "oqueue" in dir(clt):
                clt.oqueue.join()
            clt.stop()

    @staticmethod
    def wait():
        for clt in Fleet.all():
            if "wait" in dir(clt):
                clt.wait()


"interface"


def __dir__():
    return (
        'Buffered',
        'Client',
        'Fleet'
    )
