
N I X T
=======


**NAME**


|
| ``nixt`` - NIXT
|


**SYNOPSIS**


::

    >>> from nixt.object import Object
    >>> from nixt.json   import dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> print(loads(dumps(o)))
    {'a': 'b'}


**DESCRIPTION**


``NIXT`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``NIXT`` contains python3 code to program objects in a functional way.
it provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.


**INSTALL**


installation is done with pipx

|
| ``$ pip install nixt``
|


**AUTHOR**

|
| ``Bart Thate`` <``nixtniet@gmail.com``>
|

**COPYRIGHT**

|
| ``NIXT`` is Public Domain.
|
