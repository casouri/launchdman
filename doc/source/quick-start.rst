Quick Start
===========

Install
-------
launchdman works for Python 3 and it wasn't written with support of Python 2 in my mind.
But, launcdman could work under Python 2 with some minor changes. If you want to use Python 2, you can just modify it a little bit.

Normally you can just install it with pip::

  pip3 install launchdman

Or you can clone it from GitHub::

  git clone https://github.com/casouri/launchdman.git


What to Read First
------------------

If you don't know about launchd(syntax, keys, etc), read through this Launchd-tutorial_ first.
Make sure to read introduction and configuration tab. It is also a good reference about how to use launchdman in some way.

Example
-------

First import the library::

  import launchdman
  # If you know what particular configurations you want
  from launchdman import <config-you-need>
  # If you hate typing launchdman a thousand times as I hate it
  # And knows what you are doing (as I do not)
  from launchdman import *


Create a job that correlate to a plist::

  job = launchdman.Job('~/LaunchAgents/com.job.user.plist')

Add some configurations to that job::

  # Label and Program are must-haves
  job.add(launchdman.Label('job'), launchdman.Program('/usr/local/bin/job'))

  # I want it to run at load
  job.add(launcddman.RunAtLoad())

Create a bunch of configurations and group them into lists::

  runAtLoad = launchdman.RunAtLoad()
  startInterval = launchdman.StartInterval().every(1).second

  configList1 = [runAtLoad, startInterval]

  startCalendarInterval = launchdman.StartCalendarInterval({'Day':1})

  configList2 = [runAtLoad, startCalendarInterval]

Now I want to use my first group of configs::

  job.clear()
  job.add(configList1)

Actually, I want to use the second group::

  job.clear()
  job.add(configList2)

Now I want to remove the config that makes my job run on load::

  job.remove(runAtLoad)

For further explaination on remove(), check out remove-explaination_.

I am happy with this job, now it's time to write it to file!::

  job.write()

Remember to load your new plist. Open terminal and type::

  launchctl load <plist-path>

If you have loaded the plist but modified it and want to load it again. You need to unload it first::

  launchctl unload <plist-path>
  launchctl load <plist-path>

For more information, go back to launchd-tutorial_ for the Operation tab.


Available Configurations
------------------------


:py:class:`Label <launchdman.__init__.Label>`

:py:class:`Program <launchdman.__init__.Program>`

:py:class:`ProgramArguments <launchdman.__init__.ProgramArguments>`

:py:class:`EnvironmentVariables <launchdman.__init__.EnvironmentVariables>`

:py:class:`StandardInPath <launchdman.__init__.StandardInPath>`

:py:class:`StandardOutPath <launchdman.__init__.StandardOutPath>`

:py:class:`StandardErrorPath <launchdman.__init__.StandardErrorPath>`

:py:class:`WorkingDirectory <launchdman.__init__.WorkingDirectory>`

:py:class:`SoftResourceLimit <launchdman.__init__.SoftResourceLimit>`

:py:class:`HardResourceLimit <launchdman.__init__.HardResourceLimit>`

:py:class:`RunAtLoad <launchdman.__init__.RunAtLoad>`

:py:class:`StartInterval <launchdman.__init__.StartInterval>`

:py:class:`StartCalendarInterval <launchdman.__init__.StartCalendarInterval>`

:py:class:`StartOnMount <launchdman.__init__.StartOnMount>`

:py:class:`WatchPaths <launchdman.__init__.WatchPaths>`

:py:class:`QueueDirecotries <launchdman.__init__.QueueDirecotries>`

:py:class:`KeepAlive <launchdman.__init__.KeepAlive>`

:py:class:`UserName <launchdman.__init__.UserName>`

:py:class:`GroupName <launchdman.__init__.GroupName>`

:py:class:`InitGroups <launchdman.__init__.InitGroups>`

:py:class:`Umask <launchdman.__init__.Umask>`

:py:class:`RootDirecotry <launchdman.__init__.RootDirecotry>`

:py:class:`AbandonProcessGroup <launchdman.__init__.AbandonProcessGroup>`

:py:class:`ExitTimeOut <launchdman.__init__.ExitTimeOut>`

:py:class:`Timeout <launchdman.__init__.Timeout>`

:py:class:`ThrottleInverval <launchdman.__init__.ThrottleInverval>`

:py:class:`LegacyTimers <launchdman.__init__.LegacyTimers>`

:py:class:`Nice <launchdman.__init__.Nice>`



Explaination of Data Structure
------------------------------


Single( )
`````````

.. _single-explaination:

Basically, every class in launcdman is a single, even Job.

A single is a type of object that contains a tag and several(or none) values.
It can parse itself like this::

  # one value
  <tag>values</tag>

  # more than one value
  <tag>
    value1
    value2
  </tag>

If ProgramArguments(a single) has two arguments(singles) '-r' and '-o', '-r' as a single parse itself like this::

  <string>-r</string>

'-o' does the same thing. So when ProgramAarguments want to parse itself, its value is not '-r' and '-o', but ``<string>-r</string>`` and ``<string>-o</string>``.

All singles can add or remove stuff to / from its value list. so Job can add/remove configs, configs can add/remove arguments, arguments can add/remove arguments of arguments.

Of course, all the configs print with <key>s. In fact, they are all Pairs, which is a subclass of Single. Pair contains a key and several values and parse itself slightly different from how single do it. And Job parse it self differently, too.
There are several other subclasses of Single, but you don't need to worry about it. launchdman takes care of the parsing.


Single.remove( )
````````````````

.. _remove-explaination:

How remove() works in launcdman is that it compares the argument(s) it got with the configs the caller has. If they equal to each other, it removes whatever the stuff is.
For example::

  arguements = launchdman.ProgramAguments('-r')

  arguments.remove('r')

remove sees that there is a '-r' object in arguments, so it removes '-r'

Not only remove() removes str and int, it can also remove Single() (for explaination of Single, see single-explaination_)

For example::

  job = launchdman.Job(RunAtLoad())
  job.remove(RunAtLoad())

remove sees that RunAtLoad() is equal to the RunAtLoad() the job has, so it removes RunAtLoad()

Now you may ask: How does remove know if two single equal to each other?

remove() knows it by checking if they prints the same(not really, but you can see it that way).
Since launchdmand manage essentially text file, as long as two single print the same, they can be viewed as the same thing(in a text file).


.. _Launchd-tutorial: http://www.launchd.info

