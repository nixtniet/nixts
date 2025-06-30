# This file is placed in the Public Domain.


"errors"


from ..thread import Errors, line


def err(event):
    nmr = 0
    for exc in Errors.errors:
        event.reply(line(exc))
        nmr += 1
    if not nmr:
        event.reply("no errors")
        return
    event.reply(f"found {nmr} errors.")
