# This file is placed in the Public Domain.


"fleet"


from nixt.fleet  import Fleet
from nixt.thread import name


from nixts.method import fmt


def flt(event):
    clts = list(Fleet.clients.values())
    try:
        event.reply(fmt(clts[int(event.args[0])]))
    except (KeyError, IndexError, ValueError):
        event.reply(",".join([name(x).split(".")[-1] for x in clts]))
