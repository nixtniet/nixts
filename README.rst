N I X T S
=========


**NAME**


|
| ``nixts`` - NIXTS
|


**SYNOPSIS**


|
| ``nixts <cmd> [key=val] [key==val]``
| ``nixts -cvaw [init=mod1,mod2]``
| ``nixts -d`` 
| ``nixts -s``
|

**DESCRIPTION**


``NIXTS`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``NIXTS`` contains python3 code to program objects in a functional way.
it provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``NIXTS`` is a python3 IRC bot, it can connect to IRC, fetch and
display RSS feeds, take todo notes, keep a shopping list and log
text. You can run it under systemd for 24/7 presence in a IRC channel.


``NIXTS`` is Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install nixts``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ nixts srv > nixts.service``
| ``$ sudo mv nixts.service /etc/systemd/system/``
| ``$ sudo systemctl enable nixts --now``
|
| joins ``#nixts`` on localhost
|


**USAGE**


use ``nixts`` to control the program, default it does nothing

|
| ``$ nixts``
| ``$``
|

see list of commands

|
| ``$ nixts cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start console

|
| ``$ nixts -c``
|

start console and run irc and rss clients

|
| ``$ nixts -c init=irc,rss``
|

list available modules

|
| ``$ nixts mod``
| ``err,flt,fnd,irc,llm,log,mbx,mdl,mod,req,rss,``
| ``rst,slg,tdo,thr,tmr,udp,upt``
|

start daemon

|
| ``$ nixts -d``
| ``$``
|

start service

|
| ``$ nixts -s``
| ``<runs until ctrl-c>``
|


**COMMANDS**


here is a list of available commands

|
| ``cfg`` - irc configuration
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**


irc

|
| ``$ nixts cfg server=<server>``
| ``$ nixts cfg channel=<channel>``
| ``$ nixts cfg nick=<nick>``
|

sasl

|
| ``$ nixts pwd <nsnick> <nspass>``
| ``$ nixts cfg password=<frompwd>``
|

rss

|
| ``$ nixts rss <url>``
| ``$ nixts dpl <url> <item1,item2>``
| ``$ nixts rem <url>``
| ``$ nixts nme <url> <name>``
|

opml

|
| ``$ nixts exp``
| ``$ nixts imp <filename>``
|


**PROGRAMMING**


``nixts`` has it's modules in the package, so edit a file in nixts/modules/<name>.py
and add the following for ``hello world``

::

    def hello(event):
        event.reply("hello world !!")


Save this and recreate the dispatch table

|
| ``$ nixts tbl > nixts/modules/tbl.py``
|

``nixts`` can execute the ``hello`` command now.

|
| ``$ nixts hello``
| ``hello world !!``
|

Commands run in their own thread and the program borks on exit, output gets
flushed on print so exceptions appear in the systemd logs. Modules can contain
your own written python3 code, see the nixts/modules directory for examples.


**FILES**

|
| ``~/.nixts``
| ``~/.local/bin/nixts``
| ``~/.local/pipx/venvs/nixts/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``nixtniet@gmail.com``>
|

**COPYRIGHT**

|
| ``NIXTS`` is Public Domain.
|
