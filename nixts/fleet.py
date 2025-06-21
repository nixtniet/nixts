# This file is placed in the Public Domain.


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
        bot = Fleet.get(evt.orig)
        bot.put(evt)

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
            clt.oqueue.join()
            clt.stop()

    @staticmethod
    def wait():
        for clt in Fleet.all():
            if "wait" in dir(clt):
                clt.wait()


def __dir__():
    return (
        'Fleet',
    )
