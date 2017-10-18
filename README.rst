.. image:: icon.png
   :height: 0.15
   :width: 0.15

launchdman
==========


launchdman is a parser and manager for launchd, the service management framework used by macOS.
If you want to schedule to run certain tasks or programs, or run them in certain conditions, launcd is what you use on macOS.
launchdman lets you build your configurations and manage(add, remove, group, etc) them on the fly.

Inspired by schedule_ module.
.. _schedule: https://github.com/dbader/schedule

Features
========

- A simple to use API for creating and managing launchd configurations.
- Very lightweight and no external dependencies.



Quick Start
===========

::

   pip3 install launchdman

::

    from launchdman import *

    # Label and Program are must-haves
    job.add(Label('job'), Program('/usr/local/bin/job'))

    # I want it to run at load
    job.add(RunAtLoad())

    # write to plist
    job.write()

    # add a configuration
    job.add(StartInterval().every(10).minute)

    # remove a configuration
    job.remove(RunAtLoad())



Documentation
=============
For documentation, check ReadTheDocs_

.. _ReadTheDocs: http://launchdman.readthedocs.io/en/latest/



Meta
====

Yuan Fu <yuan.k.fu@gmail.com>

Feel free to ask me if you have any questions.


License
=======

Distributed under MIT license. See LICENSE.txt for more information.
