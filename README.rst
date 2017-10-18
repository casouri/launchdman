launchdman
==========


launchdman is a parser and manager for launchd, the service management framework used by macOS.
If you want to schedule to run certain tasks or programs, or run them in certain conditions, launcd is what you use on macOS.
launchdman lets you build your configurations and manage(add, remove, group, etc) them on the fly.

If you have any questions, feel free to ask me<yuan.k.fu@gmail.com> or submit issues on GitHub: https://github.com/casouri/launchdman

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
For documentation, go to ReadTheDocs_

.. _ReadTheDocs: http://launchdman.readthedocs.io/en/latest/
