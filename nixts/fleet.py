# This file is placed in the Public Domain.


"fleet"


import threading


dispatchlock = threading.RLock()
displaylock  = threading.RLock()


class Fleet:

    clients = {}
    missed  = []

    @staticmethod
    def add(clt):
        Fleet.clients[repr(clt)] = clt

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(txt):
        for clt in Fleet.clients.values():
            clt.announce(txt)

    @staticmethod
    def dispatch(evt):
        with dispatchlock:
            while True:
                for clt in Fleet.clients.values():
                    if clt.queue.empty():
                        clt.put(evt)
                        return

    @staticmethod
    def display(evt):
        with displaylock:
            clt = Fleet.get(evt.orig)
            for tme in sorted(evt.result):
                clt.say(evt.channel, evt.result[tme])

    @staticmethod
    def first():
        clt =  list(Fleet.clients.values())
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
    def wait():
        for clt in Fleet.clients.values():
            if "wait" in dir(clt):
                clt.wait()


def __dir__():
    return (
        'Fleet',
    )
