# This file is placed in the Public Domain.


"persistence"


import json.decoder
import pathlib
import _thread


from .object import update
from .serial import dump, load


class Error(Exception):

    pass


lock = _thread.allocate_lock()


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                raise Error(path) from ex


def write(obj, path):
    with lock:
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        return path


def __dir__():
    return (
        'Error',
        'cdir',
        'read',
        'write'
    )
