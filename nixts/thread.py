# This file is placed in the Public Domain.


"threading"


import queue
import time
import threading
import traceback
import _thread


launchlock = threading.RLock()
lock = threading.RLock()


class Thread(threading.Thread):

    def __init__(self, func, thrname, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, thrname, (), daemon=daemon)
        self.name = thrname or kwargs.get("name", name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.stopped = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def run(self):
        func, args = self.queue.get()
        self.result = func(*args)

    def join(self, timeout=None):
        super().join(timeout)
        return self.result


def hook(args):
    traceback.print_exception(*args[:-1])
    _thread.interrupt_main()


threading.excepthook = hook


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


"interface"


def __dir__():
    return (
        'Thread',
        'launch',
        'name'
    )
