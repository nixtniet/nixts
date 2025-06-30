# This file is placed in the Public Domain.


"fleet"


from ..fleet  import Fleet
from ..thread import name
from .        import fmt


def flt(event):
    clts = list(Fleet.clients.values())
    try:
        event.reply(fmt(clts[int(event.args[0])]))
    except (KeyError, IndexError, ValueError):
        event.reply(",".join([name(x).split(".")[-1] for x in clts]))
