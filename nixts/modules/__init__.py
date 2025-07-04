# This file is placed in the Public Domain.


"commands"


import hashlib
import importlib
import importlib.util
import inspect
import logging
import os
import sys
import threading
import time
import _thread


from ..client  import Client
from ..fleet   import Fleet
from ..object  import Object, keys
from ..persist import Workdir, skel
from ..thread  import launch


STARTTIME = time.time()


lock  = _thread.allocate_lock()
path = os.path.dirname(__file__)


CHECKSUM = "5206bffdc9dbf7a0967565deaabc2144"
CHECKSUM = ""
MD5      = {}
NAMES    = {}


class Default(Object):

    def __getattr__(self, key):
        if key not in self:
            setattr(self, key, "")
        return self.__dict__.get(key, "")


class Main(Default):

    debug   = False
    gets    = Default()
    ignore  = ""
    init    = ""
    level   = "debug"
    md5     = True
    name    = __name__.split(".", maxsplit=1)[0]
    opts    = Default()
    otxt    = ""
    sets    = Default()
    verbose = False
    version = 340


def setwd(name, path=""):
    Main.name = name
    path = path or os.path.expanduser(f"~/.{name}")
    Workdir.wdr = path
    skel()


class Event(Object):

    def __init__(self):
        Object.__init__(self)
        self._ready  = threading.Event()
        self._thr    = None
        self.channel = ""
        self.ctime   = time.time()
        self.orig    = ""
        self.rest    = ""
        self.result  = {}
        self.type    = "event"
        self.txt     = ""

    def done(self):
        self.reply("ok")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        self._ready.wait()
        if self._thr:
            self._thr.join()

class Commands:

    cmds  = {}
    md5   = {}
    names = {}

    @staticmethod
    def add(func, mod=None):
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__.split(".")[-1]

    @staticmethod
    def get(cmd):
        func = Commands.cmds.get(cmd, None)
        if not func:
            name = Commands.names.get(cmd, None)
            if not name:
                return None
            if Main.md5 and not check(name):
                return None
            mod = load(name)
            if mod:
                Commands.scan(mod)
                func = Commands.cmds.get(cmd)
        return func

    @staticmethod
    def scan(mod):
        for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmdz.__code__.co_varnames:
                Commands.add(cmdz, mod)


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if not func:
        evt.ready()
        return
    func(evt)
    Fleet.display(evt)


def inits(names):
    modz = []
    for name in sorted(spl(names)):
        mod = load(name)
        if not mod:
            continue
        if "init" in dir(mod):
            thr = launch(mod.init)
            modz.append((mod, thr))
    return modz


def parse(obj, txt=""):
    if txt == "":
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args   = []
    obj.cmd    = ""
    obj.gets   = Default()
    obj.index  = None
    obj.mod    = ""
    obj.opts   = ""
    obj.result = {}
    obj.sets   = Default()
    obj.silent = Default()
    obj.txt    = txt
    obj.otxt   = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            setattr(obj.silent, key, value)
            setattr(obj.gets, key, value)
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


"imports"


def check(name, md5=""):
    if not CHECKSUM:
        return True
    mname = f"{__name__}.{name}"
    if sys.modules.get(mname):
        return True
    pth = os.path.join(path, name + ".py")
    spec = importlib.util.spec_from_file_location(mname, pth)
    if not spec:
        return False
    if md5sum(pth) == (md5 or MD5.get(name, "")):
        return True
    if CHECKSUM and Main.md5:
        rlog("error", f"{name} md5sum failed.")
    return False


def gettbl():
    pth = os.path.join(path, "tbl.py")
    if not os.path.exists(pth):
        rlog("error", "tbl.py is not there.")
        return {}
    if CHECKSUM and (md5sum(pth) != CHECKSUM):
        rlog("error", "tbl.py checksum failed.")
        return {}
    mname = f"{__name__}.tbl"
    mod = sys.modules.get(mname, None)
    if not mod:
        spec = importlib.util.spec_from_file_location(mname, pth)
        if not spec or not spec.loader:
            return {}
        mod = importlib.util.module_from_spec(spec)
        if mod:
            spec.loader.exec_module(mod)
            sys.modules[mname] = mod
    return mod


def load(name):
    with lock:
        if name in Main.ignore:
            return None
        mname = f"{__name__}.{name}"
        module = sys.modules.get(mname, None)
        if module:
            return module
        pth = os.path.join(path, f"{name}.py")
        if not os.path.exists(pth):
            return None
        spec = importlib.util.spec_from_file_location(mname, pth)
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        if not module:
            return None
        spec.loader.exec_module(module)
        sys.modules[mname] = module
        if Main.debug:
            module.DEBUG = True
        return module


def md5sum(modpath):
    with open(modpath, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return str(hashlib.md5(txt).hexdigest())


def mods(names=""):
    res = []
    for nme in modules():
        if names and nme not in spl(names):
            continue
        mod = load(nme)
        if not mod:
            continue
        res.append(mod)
    return res


def modules():
    return sorted([
                   x[:-3] for x in os.listdir(path)
                   if x.endswith(".py") and not x.startswith("__") and
                   x[:-3] not in Main.ignore
                  ])


def settable():
    Commands.names.update(table())


def table():
    tbl = gettbl()
    MD5.update(getattr(tbl, "MD5", {}))
    NAMES.update(getattr(tbl, "NAMES", {}))
    return NAMES


"utilities"


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    yeas = int(nsec/yea)
    nsec -= yeas*yea
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def spl(txt):
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = [txt, ]
    return [x for x in result if x]


"logging"


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'warn': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
         }


def level(loglevel="debug"):
    if loglevel != "none":
        format_short = "%(message)-80s"
        datefmt = '%H:%M:%S'
        logging.basicConfig(stream=sys.stderr, datefmt=datefmt, format=format_short)
        logging.getLogger().setLevel(LEVELS.get(loglevel))


def rlog(loglevel, txt, ignore=None):
    if ignore is None:
        ignore = []
    for ign in ignore:
        if ign in str(txt):
            return
    logging.log(LEVELS.get(loglevel), txt)


"methods"


def edit(obj, setter, skip=True):
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def fmt(obj, args=None, skip=None, plain=False, empty=False):
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if not empty and not value:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str):
            txt += f'{key}="{value}" '
        else:
            txt += f'{key}={value} '
    return txt.strip()


"interface"


def __dir__():
    return (
        'Commands',
        'Default',
        'Main',
        'command',
        'edit',
        'elapsed',
        'fmt',
        'inits',
        'level',
        'load',
        'parse',
        'rlog',
        'spl'
    )
