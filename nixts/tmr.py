# This file is placed in the Public Domain.


"timers"


import datetime
import re
import time


from nixt.client  import Fleet
from nixt.find    import last
from nixt.object  import Object, items
from nixt.persist import write
from nixt.timer   import Timed


from . import elapsed, rlog


class NoDate(Exception):

    pass


class Timers(Object):

    def add(self, timer):
        setattr(self, str(timer.target), (timer.func, timer.args))


timers = Timers()


def init():
    pth = last(timers)
    remove = []
    for tme, tmr in items(timers):
        diff = float(tme) - time.time()
        if diff > 0:
            timer = Timed(diff, Fleet.announce, tmr[1][-1])
            timer.start()
            rlog("debug", f"timer at {time.ctime(float(tme))}")
        else:
            remove.append(tme)
    for tme in remove:
        delattr(timers, tme)
    write(timers, pth)


def extract_date(daystr):
    daystr = daystr.encode('utf-8', 'replace').decode("utf-8")
    res = time.time()
    for fmt in FORMATS:
        try:
            res = time.mktime(time.strptime(daystr, fmt))
            break
        except ValueError:
            pass
    return res


def get_day(daystr):
    day = None
    month = None
    yea = None
    try:
        ymdre = re.search(r'(\d+)-(\d+)-(\d+)', daystr)
        if ymdre:
            (day, month, yea) = ymdre.groups()
    except ValueError:
        try:
            ymre = re.search(r'(\d+)-(\d+)', daystr)
            if ymre:
                (day, month) = ymre.groups()
                yea = time.strftime("%Y", time.localtime())
        except Exception as ex:
            raise NoDate(daystr) from ex
    if day:
        day = int(day)
        month = int(month)
        yea = int(yea)
        date = f"{day} {MONTHS[month]} {yea}"
        return time.mktime(time.strptime(date, r"%d %b %Y"))
    raise NoDate(daystr)


def get_hour(daystr):
    try:
        hmsre = re.search(r'(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hmsres = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search(r'(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hmsres = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hmsres


def get_time(txt):
    try:
        target = get_day(txt)
    except NoDate:
        target = to_day(today())
    hour =  get_hour(txt)
    if hour:
        target += hour
    return target


def parse_time(txt):
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = get_day(txt)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(txt)
        if hour:
            target += hour
    return target


def to_day(daystr):
    previous = ""
    line = ""
    daystr = str(daystr)
    res = None
    for word in daystr.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_date(line.strip())
            break
        except ValueError:
            res = None
        line = ""
    return res


def today():
    return str(datetime.datetime.today()).split()[0]


def tmr(event):
    result = ""
    if not event.rest:
        nmr = 0
        for tme, obj in items(timers):
            lap = float(tme) - time.time()
            if lap > 0:
                event.reply(f'{nmr} {obj[-1][-1]} {elapsed(lap)}')
                nmr += 1
        if not nmr:
            event.reply("no timers.")
        return result
    seconds = 0
    line = ""
    for word in event.args:
        if word.startswith("+"):
            try:
                seconds = int(word[1:])
            except (ValueError, IndexError):
                event.reply(f"{seconds} is not an integer")
                return result
        else:
            line += word + " "
    if seconds:
        target = time.time() + seconds
    else:
        try:
            target = get_day(event.rest)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(event.rest)
        if hour:
            target += hour
    if not target or time.time() > target:
        event.reply("already passed given time.")
        return result
    pth = last(timers)
    diff = target - time.time()
    txt = " ".join(event.args[1:])
    timer = Timed(diff, Fleet.say, event.orig, event.channel, txt)
    timer.target = target
    timers.add(timer)
    write(timers, pth)
    timer.start()
    event.reply("ok " +  elapsed(diff))


MONTHS = [
    'Bo',
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
]


FORMATS = [
    "%Y-%M-%D %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
]
