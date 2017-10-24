from setuptools import setup

setup(
    name='launchdman',
    version='0.1.1',
    description='The launchd parser and manager for Python',
    long_description=
    '''launchdman is a parser and manager for launchd, the service management framework used by macOS.
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


''',
    url='https://github.com/casouri/launchdman',
    download_url='https://github.com/casouri/launchdman/archive/0.1.tar.gz',
    author='Yuan Fu',
    author_email='yuan.k.fu@gmail.com',
    license='MIT',
    packages=['launchdman'],
    python_requires='>=3', )
