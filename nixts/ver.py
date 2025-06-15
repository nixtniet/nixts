# This file is placed in the Public Domain.


"version"


from . import Main


def ver(event):
    event.reply(str(Main.version))
