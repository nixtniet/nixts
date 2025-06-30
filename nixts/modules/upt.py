# This file is placed in the Public Domain.


"uptime"


import time


from ..command import STARTTIME
from ..utility import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
