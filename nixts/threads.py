# This file is placed in the Public Domain.


"threading"


import queue
import time
import threading
import traceback
import _thread


launchlock = threading.RLock()
lock       = threading.RLock()


class Thread(threading.Thread):

    def __init__(self, func, thrname, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, thrname, (), daemon=daemon)
        self.name      = thrname or kwargs.get("name", name(func))
        self.queue     = queue.Queue()
        self.result    = None
        self.starttime = time.time()
        self.stopped   = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def run(self):
        try:
            func, args = self.queue.get()
            self.result = func(*args)
        except Exception as ex:
            later(ex)
            try:
                args[0].ready()
            except (IndexError, AttributeError):
                pass
            _thread.interrupt_main()

    def join(self, timeout=0.0):
        super().join(timeout)
        return self.result


def launch(func, *args, **kwargs):
    with launchlock:
        nme = kwargs.get("name", None)
        if not nme:
            nme = name(func)
        thread = Thread(func, nme, *args, **kwargs)
        thread.start()
        return thread


def name(obj):
    typ = type(obj)
    if '__builtins__' in dir(typ):
        return obj.__name__
    if '__self__' in dir(obj):
        return f'{obj.__self__.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    return ""


"timers"


class Timy(threading.Timer):

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__(sleep, func)
        self.name               = kwargs.get("name", name(func))
        self.sleep              = sleep
        self.state              = {}
        self.state["latest"]    = time.time()
        self.state["starttime"] = time.time()
        self.starttime          = time.time()


class Timed:

    def __init__(self, sleep, func, *args, thrname="", **kwargs):
        self.args   = args
        self.func   = func
        self.kwargs = kwargs
        self.sleep  = sleep
        self.name   = thrname or kwargs.get("name", name(func))
        self.target = time.time() + self.sleep
        self.timer  = None

    def run(self):
        self.timer.latest = time.time()
        self.func(*self.args)

    def start(self):
        self.kwargs["name"] = self.name
        timer = Timy(self.sleep, self.run, *self.args, **self.kwargs)
        timer.start()
        self.timer = timer

    def stop(self):
        if self.timer:
            self.timer.cancel()


class Repeater(Timed):

    def run(self):
        launch(self.start)
        super().run()


"errors"


class Errors:

    name   = __file__.rsplit("/", maxsplit=2)[-2]
    errors = []


def full(exc):
    with lock:
        return "".join(
                       traceback.format_exception(
                                                  type(exc),
                                                  exc,
                                                  exc.__traceback__
                                                 )
                      ).rstrip()


def later(exc):
    with lock:
        Errors.errors.append(exc)


def line(exc):
    exctype, excvalue, trb = type(exc), exc, exc.__traceback__
    trace = traceback.extract_tb(trb)
    result = ""
    for i in trace:
        fname = i[0]
        if fname.endswith(".py"):
            fname = fname[:-3]
        linenr = i[1]
        plugfile = fname.split("/")
        mod = []
        for ii in list(plugfile[::-1]):
            mod.append(ii)
            if Errors.name in ii or "bin" in ii:
                break
        ownname = '.'.join(mod[::-1])
        if ownname.endswith("__"):
            continue
        if ownname.startswith("<"):
            continue
        result += f"{ownname}:{linenr} "
    del trace
    res = f"{exctype} {result[:-1]} {excvalue}"
    if "__notes__" in dir(exc):
        for note in exc.__notes__:
            res += f" {note}"
    return res


"interface"


def __dir__():
    return (
        'Errors',
        'Repeater',
        'Thread',
        'Timed',
        'full',
        'later',
        'launch',
        'line',
        'name'
    )
