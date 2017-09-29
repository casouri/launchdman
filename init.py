from pathlib import Path
import __main__
import os
from copy import copy
from conditions import *


# MARK: Functions
# MARK: Working
def parse(element):
    pass


def add(rule, outList):
    for valueElement in rule['value']:
        try:
            # see if the object on which function called contains
            # other Rule object in its value
            lowerRule = valueElement['value']
            add(lowerRule, outList)
            return
        except:
            outList.insert(0, parse(rule['key'], valueElement))
            return


# MARK: Classes
class Job():

    # MARK: Properties
    me = Path(__file__)
    myPath = me.absolute
    dirPath = me.parent

    programArguments = []

    # MARK: Functions
    def addon(condition):
        self.conditionList.append(condition) @ property


def label(self):
    condition = Label()
    return condition


@property
def program(self):
    condition = Program()
    return condition


@property
def programArguments(self):
    condition = ProgramArguments()
    return condition


@property
def environmentVariables(self):
    condition = EnvironmentVariables()
    return condition


@property
def standardInPath(self):
    condition = StandardInPath()
    return condition


@property
def standardOutPath(self):
    condition = StandardOutPath()
    return condition


@property
def standardErrorPath(self):
    condition = StandardErrorPath()
    return condition


@property
def workingDirectory(self):
    condition = WorkingDirectory()
    return condition


@property
def softResourceLimit(self):
    condition = SoftResourceLimit()
    return condition


@property
def hardResourceLimit(self):
    condition = HardResourceLimit()
    return condition


@property
def runAtLoad(self):
    condition = RunAtLoad()
    return condition


@property
def startInterval(self):
    condition = StartInterval()
    return condition


@property
def startCalendarInterval(self):
    condition = StartCalendarInterval()
    return condition


@property
def startOnMount(self):
    condition = StartOnMount()
    return condition


@property
def watchPath(self):
    condition = WatchPath()
    return condition


@property
def queueDirecotries(self):
    condition = QueueDirecotries()
    return condition


@property
def keepAlive(self):
    condition = KeepAlive()
    return condition


@property
def userName(self):
    condition = UserName()
    return condition


@property
def groupName(self):
    condition = GroupName()
    return condition


@property
def initGroups(self):
    condition = InitGroups()
    return condition


@property
def umask(self):
    condition = Umask()
    return condition


@property
def rootDirecotry(self):
    condition = RootDirecotry()
    return condition


@property
def abandonProcessGroup(self):
    condition = AbandonProcessGroup()
    return condition


@property
def exitTimeOut(self):
    condition = ExitTimeOut()
    return condition


@property
def timeout(self):
    condition = Timeout()
    return condition


@property
def throttleInverval(self):
    condition = ThrottleInverval()
    return condition


@property
def legacyTimers(self):
    condition = LegacyTimers()
    return condition


@property
def nice(self):
    condition = Nice()
    return condition
