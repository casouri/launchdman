import textwrap
from collections import Iterable
from pathlib import Path


def checkKey(key, keyList):
    if key not in keyList:
        raise AttributeError('"{}" is not a valid key'.format(key))


def indent(text, amount, ch=' '):
    '''take test and indent every line by amount characters

    Args:
        text (str): The test to be indented
        amount (int): The amount of indentation
        ch (str): Default to be a space(' '). This is what to use when indenting the text.

    Example:

    >>> indent('Mary had a little lamb', 4, '$')
    >>> '$$$$Mary had a little lamb'


    Returns:
        str: The indented text


    '''
    return textwrap.indent(text, amount * ch)


def flatten(l):
    '''Flatten a multi-deminision list and return a iterable

    Note that dict and str will not be expanded, instead, they will be kept as a single element.

    Args:
        l (list): The list needs to be flattened

    Returns:
        A iterable of flattened list. To have a list instead use ``list(flatten(l))``
    '''
    for el in l:
        # I don;t want dict to be flattened
        if isinstance(el, Iterable) and not isinstance(
                el, (str, bytes)) and not isinstance(el, dict):
            yield from flatten(el)
        else:
            yield el


def crossCombine(l):
    ''' Taken a list of lists, returns a big list of lists contain all the possibilities of elements of sublist combining together.

    It is basically a Combinatorics of list. For example:

        >>> crossCombine([[a,a1,a2,...], [b,b1,b2,...]])
        >>> [[a,b], [a,b1], [a,b2], [a1,b], [a1,b1], [a1, b2], [a2,b], [a2,b1], [a2,b2], ...]

    For using in StartCalendarInterval, the syntax of ``l`` is like below:
        ``l: [[dic of month], [dict of day]]``

    such as:
        ``l: [[{'month': 1}, {'month': 2}], [{'day': 2}, {'day': 3}, {'day': 4}]]``

    Args:
        l (list[list]): the list of lists you want to crossCombine with.

    Returns:
        list: crossCombined list

    '''
    resultList = []
    firstList = l[0]
    rest = l[1:]
    if len(rest) == 0:
        return firstList
    for e in firstList:
        for e1 in crossCombine(rest):
            resultList.append(combinteDict(e, e1))
    return resultList


def combine(a1, a2):
    ''' Combine to argument into a single flat list

    It is used when you are not sure whether arguments are lists but want to combine them into one flat list

    Args:
        a1: list or other thing
        a2: list or other thing

    Returns:
        list: a flat list contain a1 and a2
    '''
    if not isinstance(a1, list):
        a1 = [a1]
    if not isinstance(a2, list):
        a2 = [a2]
    return a1 + a2


def combinteDict(d, d1):
    '''Combine two dict into one

    Example:

    >>> combinteDict({'1': 1}, {'2': 2})
    >>> {'1': 1, '2': 2}

    Args:
        d (dict): A dict to combine with
        d1 (dict): A dict to combine with

    Returns:
        dict: the combined dict
    '''
    return {**d, **d1}


def ancestor(obj):
    '''Trace the parent tree of the object and return the second last one.(under object)

    Args:
        obj (object): Literally anything.

    Returns:
        class: a class object
    '''
    return list(obj.__class__.__mro__)[-2]


def ancestorJr(obj):
    '''Trace the parent tree of the object and return the third last one.(under object and anothr parent)

    Args:
        obj (object): Literally anything.

    Returns:
        class: a class object
    '''
    return list(obj.__class__.__mro__)[-3]


def singleOrPair(obj):
    '''Chech an object is single or pair or neither.

    Of course,, all pairs are single, so what the function is really detecting is whether an object is only single or at the same time a pair.

    Args:
        obj (object): Literally anything.

    Returns:
        str: 'Single', or 'Pair', or 'Neither'
    '''
    if len(list(obj.__class__.__mro__)) <= 2:
        return 'Neither'
    else:
        # Pair check comes first for Pair is a subclass of Single
        if ancestorJr(obj) is Pair:
            return 'Pair'
        elif ancestor(obj) is Single:
            return 'Single'
        else:
            return 'Neither'


def removeEverything(toBeRemoved, l):
    '''Remove every instance that matches the input from a list

    Match with ==, operation, which can be defined in __eq__.

    Args:
        tobeRemoved (object): the same object you want to remove from the list.
        l (list): the llist you want to remove stuff from.
    '''
    successful = True
    while successful:
        try:
            # list.remove will remove item if equal,
            # which is evaluated by __eq__
            l.remove(toBeRemoved)
        except:
            successful = False


class Single():
    '''
    A type of structure that only have a tag and it's values.
    It is parsed sush as ::

        <tag>value</tag> # for on value element and

        <tag>
            value1
            value2
        </tag> # for multiple value element

    Overwrite ``printMe(tag, value)`` if subclass parse differently from Single.

    Properties:
        tag (string): the tag
        value (list): A list of values. element can be Single and any subclass of it, string, integer. Other data type might be possible, but not used in launchd files.
    '''
    tag = ''
    value = []

    def __eq__(self, other):
        return set(self.findAll(self.value)) == set(other.findAll(other.value))

    def __init__(self, tag, *value):
        '''init

        Args:
            tag (str): The tag1
            *value: the elements you want to put into single's value(list), can be one element or several seperate by comma, or put into a list or combination of those. *value will be flattend to a single one deminision list. In subclasses' init, raw data should be converted to single if needed according to specific subclass.'''
        self.tag = tag
        self.value = list(flatten(value))

    def parse(self):
        '''A wrap of PrintMe, which parse the single and its value and returns a str. In most cases, this is the method you need to use.'''
        return self.printMe(self.tag, self.value)

    def printMe(self, selfTag, selfValue):
        '''Parse the single and its value and return the parsed str.

        Args:
           selfTag (str): The tag. Normally just ``self.tag``
           selfValue (list): a list of value elements(single, subclasses, str, int). Normally just ``self.value``

        Returns:
            str: A parsed text
        '''
        if len(selfValue) == 0:
            return ''
        # if value have only one element and it is not another single
        # print differently
        elif len(selfValue) == 1 and not ancestor(selfValue[0]) is Single:
            text = '<{tag}>{value}</{tag}>\n'.format(
                tag=selfTag, value=selfValue[0])
            return text
        else:
            valueText = ''
            for element in selfValue:
                # if the element is another single
                # or merely an object
                # both possibility should not happen in the same time
                # if so, user is not doing the right thing
                if singleOrPair(element) == 'Single':
                    # ask that single to print itself
                    valueText += element.printMe(element.tag, element.value)
                elif singleOrPair(element) == 'Pair':
                    valueText += element.printMe(element.key, element.value)
                else:
                    # simply print that element
                    valueText += str(element) + '\n'
            valueText = indent(valueText, 4)
            text = '<{tag}>\n'.format(
                tag=selfTag) + valueText + '</{tag}>\n'.format(tag=selfTag)
            return text

    def findAll(self, selfValue):
        '''Looks for all the non single values(str, int) *recursively* and returns a list of them

        Args:
            selfValue: A list of single, str, int. Normally just ``self.value``

        Returns:
            list: A list contains only non singles(str, int).
        '''
        resultList = []
        for element in selfValue:
            if isinstance(element, Single):
                resultList += element.findAll(element.value)
            else:
                resultList.append(element)
        return resultList

    def findAllSingle(self, selfValue):
        '''Looks for all the single values and subclasses *recursively* and returns a list of them

        Args:
            selfValue: A list of single, str, int. Normally just ``self.value``

        Returns:
            list: A list contains only singles and subclasses.
        '''
        resultList = []
        for element in selfValue:
            if isinstance(element, Single):
                resultList.append(element)
                resultList += element.findAllSingle()
        return resultList

    def _add(self, value, selfValue):
        '''Add a element to a list. Used inside add() method.

        Subclass are responsible of creating whatever single instance it need
        from its add(*value) and call _add() with it.

        Args:
            value: single, str, int. Any thing that can be in single.value
            self.Value (list): the list to add into.
        '''
        selfValue += value
        return (value)

    def add(self, *value):
        '''convert value and add to self.value

        Subclass must overwrite this method.
        Subclass are responsible of creating whatever single instance it need from its ``add(*value)`` and call ``_add()`` to add them to ``self.value``

        Args:
            *value: the value to be added
        '''
        flattenedValueList = list(flatten(value))
        return self._add(flattenedValueList, self.value)

    def _remove(self, removeList, selfValue):
        '''Remove elements from a list by matching the elements in the other list.

        This method only looks inside current instance's value, not recursive.
        There is no need for a recursive one anyway.
        Match by == operation.

        Args:
            removeList (list): The list of matching elements.
            selfValue (list): The list you remove value from. Usually ``self.value``
        '''
        for removeValue in removeList:
            print(removeValue, removeList)
            # if removeValue equal to selfValue, remove
            removeEverything(removeValue, selfValue)

    def remove(self, *l):
        ''' remove elements from self.value by matching.

        Create the exactly same single you want to delete and pass it(them) in.
        Normally this method needs to be overwrited by subclass. It only looks inside current instance's value, not recursive. There is no need for a recursive one anyway.

        Args:
            *l: a single element, a bunch of element seperated by comma, or a list of elements, or any combination. Element is what you match with.
        '''
        removeList = list(flatten(l))
        self._remove(removeList, self.value)

    def clear(self):
        '''Remove everything in a Single'''
        self.value = []


class Job(Single):
    '''Each Job is correspond to a plist.'''

    def __init__(self, path):
        '''init

        Args:
            path (str): The absolute path of the plist
        '''
        self.me = Path(path)
        self.tag = 'dict'
        self.value = []

    def write(self):
        '''Write the job to the corresponding plist.'''
        with open(self.me, 'w') as f:
            f.write(self.printMe(self.tag, self.value))

    def printMe(self, selfTag, selfValue):
        '''Parse the job into plist format.

        Args:
            selfTag (str): The tag. Usually ``self.tag``
            selfValue (list): The value list. Usually ``self.value``'''
        if len(selfValue) == 0:
            return ''
        else:
            valueText = ''
            for element in selfValue:
                # if the element is another single
                # or merely an object
                # both possibility should not happen in the same time
                # if so, user is not doing the right thing
                if singleOrPair(element) == 'Single':
                    # ask that single to print itself
                    valueText += element.printMe(element.tag, element.value)
                elif singleOrPair(element) == 'Pair':
                    valueText += element.printMe(element.key, element.value)
                else:
                    # simply print that element
                    valueText += str(element) + '\n'
            valueText = indent(valueText, 4)
            text = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<{tag}>\n'.format(
                tag=selfTag) + valueText + '</{tag}>\n</plist>'.format(
                    tag=selfTag)
            return text


class BoolSingle(Single):
    '''A type of Single that only have a single tag that usually indicate true of false.

    Example::

        </true>
        <false>
    '''

    def __init__(self, boolValue):
        '''init

        Args:
            bollValue (str): The boolean value of the single. It can be either ``'true'`` or ``'false'``
        '''
        self.value = [boolValue]

    def printMe(self, selfTag='', selfValue='true'):
        text = '<{value}/>\n'.format(value=selfValue[0])
        return text


class TypedSingle(Single):
    '''A little sugar so that you don't need to type the tag every time creating a specific single.
    This class is meant to be inheritated by specific type single classes such as arraySingle and StringSingle. The class name of subclass will become the tag. For example::

        ArraySingle.tag -> 'array'
    '''

    def __init__(self, *value):
        '''init

        set self.tag to classname. e.g.::

            ArraySingle.tag -> 'array'

        Args:
            *value: the elements you want to put into single's value(list), can be one element or several seperate by comma, or put into a list or combination of those. *value will be flattend to a single one deminision list. In subclasses' init, raw data should be converted to single if needed according to specific subclass.'''
        tag = self.__class__.__name__.replace('Single', '').lower()
        super().__init__(tag, value)


class StringSingle(TypedSingle):
    '''Single with default tag as 'string'.'''
    pass


class ArraySingle(TypedSingle):
    '''Single with default tag as 'array'.'''
    pass


class DictSingle(TypedSingle):
    '''Single with default tag as 'dict'.'''
    pass


class IntegerSingle(TypedSingle):
    '''Single with default tag as 'integer'.'''
    pass


class Pair(Single):
    '''A data type that have a key and it's value.
    For example::

        <key>some_key</key> # some_key is the key
        <array> # array is the value
            <string>something</string>
        </array>
    '''
    key = ''
    value = []

    def __init__(self, key='', *value):
        '''init

        Args:
            key (str): the key
            *value: the value to be stored
        '''
        if key == '':
            self.key = self.__class__.__name__
        else:
            self.key = key
        if len(value) != 0:
            self.value = list(flatten(value))

    def parse(self):
        '''parse the pair in plist format.
        A wrapper of printMe().

        Returns:
            str: the parsed text
           '''
        return self.printMe(self.key, self.value)

    def printMe(self, selfKey, selfValue):
        '''Parse the single and its value and return the parsed str.

        Args:
           selfTag (str): The tag. Normally just ``self.tag``
           selfValue (list): a list of value elements(single, subclasses, str, int). Normally just ``self.value``

        Returns:
            str: A parsed text
        '''
        text = '<key>{keyName}</key>\n'.format(keyName=selfKey)

        if len(selfValue) == 0:
            return ''
        else:
            valueText = ''
            for element in selfValue:
                if singleOrPair(element) == 'Single':
                    valueText += element.printMe(element.tag, element.value)
                elif singleOrPair(element) == 'Pair':
                    valueText += element.printMe(element.key, element.value)
                # maybe a else statement for non single non pair?

        text += valueText
        return text


class SingleStringPair(Pair):
    '''Pair that conntains only a string in its value.

    Since there is only a single element in value. ``add()`` and ``remove()`` is not needed.
    Instead there is a ``changTo()`` method.
    '''

    def __init__(self, string):
        '''init

        Args:
            string (str): The string you want the value element to be
        '''
        super().__init__()
        self.changeTo(string)

    def changeTo(self, newString):
        '''This method change the value element of the Pair.

        Args:
            newString (str): The string you want to change to
        '''
        self.value = [StringSingle(newString)]


class SingleIntegerPair(Pair):
    '''The Pair that contains only a integer.

    Since there is only a single element in value. ``add()`` and ``remove()`` is not needed.
    Instead there is a ``changTo()`` method.
    '''

    def __init__(self, integer):
        super().__init__()
        self.changeTo(integer)

    def changeTo(self, newInt):
        '''This method change the value element of the Pair.

        Args:
            newInt (int): The integer you want to change to
        '''
        self.value = [IntegerSingle(newInt)]


class OuterOFInnerPair(Pair):
    '''A "double layer" Pair.
    e.g.: array of string, dict of pair, array of bool
    Outer can be: ArraySingle, DictSingle
    Inner can be: Pair, StringSingle, IntegerSingle, BoolPair
    '''

    def __init__(self, Outer, Inner, *l):
        '''init

        Args:
            Outer (class): One of the possible outer classes.
            Inner (class): One of the possible inner classes.
            *l: To be processed and set to value
        '''
        super().__init__()
        self.value = [Outer()]
        self.l = self.value[0].value
        self.Outer = Outer
        self.Inner = Inner
        self.add(l)

    def add(self, *l):
        '''add inner to outer

        Args:
            *l: element that is passed into Inner init
        '''
        for a in flatten(l):
            self._add([self.Inner(a)], self.l)

    def remove(self, *l):
        '''remove inner from outer

        Args:
            *l element that is passes into Inner init
        '''
        for a in flatten(l):
            self._remove([self.Inner(a)], self.l)


class BoolPair(Pair):
    '''A special type of pair that contains it's key and only one tag, usually </true> or </false>.'''

    def __init__(self, key=''):
        '''init

        set value to true

        Args:
        key (str): either 'true' or 'false'
        '''
        super().__init__(key)
        self.setToTrue()

    def setToTrue(self):
        '''This method sets the value of key true.'''
        self.value = [BoolSingle('true')]

    def setToFalse(self):
        '''Might be needed, set value to false.'''
        self.value = [BoolSingle('false')]

    def add(self):
        pass

    def remove(self):
        pass

    def _add(self):
        pass

    def _remove(self):
        pass


class SingleDictPair(Pair):
    '''Pair that contains one DictSingle(which contains pairs) in its value.'''

    def __init__(self, dic):
        '''init

        Args:
            dic (dict): key and value
        '''
        super().__init__()
        self.value = [DictSingle()]
        self.d = self.value[0].value
        self.add(dic)

    def add(self, dic):
        '''adds a dict as pair

        Args:
            dic (dict): key and value
        '''
        for kw in dic:
            checkKey(kw, self.keyWord)
            self._add([Pair(kw, StringSingle(dic[kw]))], self.d)

    def remove(self, dic):
        '''remove the pair by passing a identical dict

        Args:
            dic (dict): key and value
        '''
        for kw in dic:
            removePair = Pair(kw, dic[kw])
            self._remove([removePair])


class Label(SingleStringPair):
    '''Label config

    Example::

        config = Label('some-label')
        config.changeTo('some-other-label')

    '''
    pass


class Program(SingleStringPair):
    '''Program config

    Example::

        config = Program('/path/to/program')
        config.changeTo('/new/path/to/program')

    '''
    pass


class ProgramArguments(OuterOFInnerPair):
    '''ProgramArguments config

    Example::

        config = ProgramArguments(['-r', '--outfile', '-m'])
        config = ProgramArguments('-r')
        config = ProgramArguments('-r', '-m', '--file')
        config.remove('-r')
        config.add('--kill')
    '''

    def __init__(self, *l):
        '''init

        Args
            *l: argument(s) you want to pass
        '''
        super().__init__(ArraySingle, StringSingle, l)


class EnvironmentVariables(Pair):
    '''EnvironmentVariables config

    Example::

        config = EnvironmentVariables('/bin:/usr/bin:/usr/local/bin')
        config.changeTo('some-other-env')

    '''

    def __init__(self, path):
        '''init

        Args:
            path (str): the environment
        '''
        super().__init__()
        self.changeTo(path)

    def changeTo(self, path):
        '''change value

        Args:
            path (str): the new environment path
        '''
        dictionary = DictSingle(Pair('PATH', StringSingle(path)))
        self.value = [dictionary]


class StandardInPath(SingleStringPair):
    '''StandardInPath config

    Example::

        config = StandardInPath('/tmp/in')
        config.changeTo('some/other/path')

    '''
    pass


class StandardOutPath(SingleStringPair):
    '''StandardOutPath config

    Example::

        config = StandardOutPath('/tmp/out')
        config.changeTo('some/other/path')

    '''
    pass


class StandardErrorPath(SingleStringPair):
    '''StandardErrorPath config

    Example::

        config = StandardErrorPath('/tmp/error')
        config.changeTo('some/other/path')

    '''
    pass


class WorkingDirectory(SingleStringPair):
    '''WorkingDirectory config

    Example::

        config = WorkingDirectory('/home')
        config.changeTo('some/other/path')

    '''
    pass


class SoftResourceLimit(SingleDictPair):
    '''SoftResourceLimit config

    Example::

        config = SoftResourceLimit({'CPU': 2, 'FileSize': 1024})
        config.add({'NumberOfFiles': 10})
        config.remove({'CPU': 2})

    Avaliable keys are: CPU, FileSize, NumberOfFiles, Core, Data, MemoryLock, NumberOfProcesses, ResidentSetSize, Stack.

    '''
    keyWord = [
        'CPU', 'FileSize', 'NumberOfFiles', 'Core', 'Data', 'MemoryLock',
        'NumberOfProcesses', 'ResidentSetSize', 'Stack'
    ]


class HardResourceLimit(SingleDictPair):
    '''HardResourceLimit config

    Example::

        config = HardResourceLimit({'CPU': 2, 'FileSize': 1024})
        config.add({'NumberOfFiles': 10})
        config.remove({'CPU': 2})

    Avaliable keys are: CPU, FileSize, NumberOfFiles, Core, Data, MemoryLock, NumberOfProcesses, ResidentSetSize, Stack.

    '''
    keyWord = [
        'CPU', 'FileSize', 'NumberOfFiles', 'Core', 'Data', 'MemoryLock',
        'NumberOfProcesses', 'ResidentSetSize', 'Stack'
    ]


class RunAtLoad(BoolPair):
    '''RunAtLoad config

    Example::

        config = RunAtLoad()
    '''
    pass


class StartInterval(Pair):
    '''StartInterval config

    Example:

        config = StartInterval().every(1).second
        config = StartInterval().every(10).day

    Avaliable time intervals are: second, minute. hour, day, week.

    '''
    baseNumber = 1
    magnification = 1

    def __init__(self):
        super().__init__()

    def every(self, baseNumber):
        '''set base number

        Args:
            baseNumber (str): number of day/minute/second/etc
        '''
        self.baseNumber = baseNumber
        return self

    def _update(self, baseNumber, magnification):
        '''update self.value with basenumber and time interval

        Args:
            baseNumber (str): self.baseNumber
            magnification (str): self.magnification
        '''
        interval = int(baseNumber * magnification)
        self.value = [IntegerSingle(interval)]

    @property
    def second(self):
        '''set unit to second'''
        self.magnification = 1
        self._update(self.baseNumber, self.magnification)
        return self

    @property
    def minute(self):
        '''set unit to minute'''
        self.magnification = 60
        self._update(self.baseNumber, self.magnification)
        return self

    @property
    def hour(self):
        '''set unit to hour'''
        self.magnification = 3600
        self._update(self.baseNumber, self.magnification)
        return self

    @property
    def day(self):
        '''set unit to day'''
        self.magnification = 86400
        self._update(self.baseNumber, self.magnification)
        return self

    @property
    def week(self):
        '''set unit to week'''
        self.magnification = 345600
        self._update(self.baseNumber, self.magnification)
        return self


class StartCalendarInterval(Pair):
    '''Set StartCalendarInterval config

    Usage:
        pass a dictionary as setting into StartCalendarInterval, possible key words are Month, Day, Weekday, Hour, Minute. *Note the uppercase.*

    For example::

        # for simple config
        schedule = StartCalendarInterval({'Day': 1, 'Month': 3}) # every March 1st

        # for more straight forward syntax, use gen()
        schedule.add(schedule.gen(day=1, month=3)) # every March 1st

        # for a interval schedule, use genInterval()
        schedule.add(schedule.genInterval(day=(1,15))) # from 1st to 15th every month

        # for more complicated(corn-like) schedule, use genMix()
        schedule.add(schedule.genMix(day=(1, 3, 5), month=(2,4)))

        schedule.add(schedule.genMix(day=tuple(range(1, 10, 2))))
        # 1st, 3rd, 5th, 7th, 9th every month

        # like other add() method, StartCalendarInterval.add() can take multiple arguments or lists
        schedule.add(schedule.gen(day=1), schedule.gen(day=15), [schedule.gen(month=12), schedule.gen(weekday=3)])



    '''
    keyWord = ['Month', 'Day', 'Weekday', 'Hour', 'Minute']

    def __init__(self, *dic):
        '''init

        Args:
            *dic (dict): dictionary with format {'Day': 12, 'Hour': 34} Avaliable keys are Month, Day, Weekday, Hour, Minute. *Note the uppercase.* You can use gen(), genMix() to generate complex config dictionary.
        '''
        super().__init__()
        self.value = [ArraySingle()]
        self.l = self.value[0].value

    def add(self, *dic):
        '''add a config to StartCalendarInterval.

        Args:
            *dic (dict): dictionary with format {'Day': 12, 'Hour': 34} Avaliable keys are Month, Day, Weekday, Hour, Minute. *Note the uppercase.* You can use gen(), genMix() to generate complex config dictionary.
        '''
        dicList = list(flatten(dic))
        # for every dict in the list passed in
        for d in dicList:
            # make a dict single (list of pairs)
            di = []
            for k in d:
                # checkKey(k, self.keyWord)
                di.append(Pair(k, IntegerSingle(d[k])))
            dictSingle = DictSingle(di)
            # append dict single to array single's value
            self._add([dictSingle], self.l)

    def remove(self, *dic):
        '''remove a calendar config.

        Args:
            *dic (dict): dictionary with format {'Day': 12, 'Hour': 34} Avaliable keys are Month, Day, Weekday, Hour, Minute. *Note the uppercase.* You can use gen(), genMix() to generate complex config dictionary.
        '''
        dicList = list(flatten(dic))
        for d in dicList:
            di = []
            for k in d:
                # checkkey(k, self.keyword)
                di.append(Pair(k, IntegerSingle(d[k])))
            dictSingle = DictSingle(di)
            # append dict single to array single
            self._remove([dictSingle], self.l)

    def gen(self, month=0, week=0, day=0, weekday=0, hour=0, minute=0):
        '''generate config dictionary to pass to add() or remove()

        Args:
            month (int): month in a year, from 1 to 12
            week (int): week in a month, from 1 to 4
            day (int): day in a month, from 1 to 31
            weekday (int): weekday in a week, from 0 to 7. 0 and 7 both represent Sunday
            hour (int): hour in a day, from 0 to 24
            minute (int): minute in an hour, from 0 to 59

        Returns:
            dict: a dictionary with form {'Day': 1, etc}
        '''
        dic = {
            'Month': month,
            'Day': day,
            'Week': week,
            'Weekday': weekday,
            'Day': day,
            'Hour': hour,
            'Minute': minute
        }
        dic = {k: v for k, v in dic.items() if v != 0}
        return dic

    def genMix(self, month=(), day=(), week=(), weekday=(), hour=(),
               minute=()):
        '''Generate a list of config dictionarie(s), in form of [{'Day':12, 'Month':3}, {}, etc]
        For example::

            genMix(month=(1, 4, 6, 8), day=tuple(range(1, 30, 2)))
            # Keep in mind that range(1, n) gives you (1, 2, ... , n-1)

        Args:
            month (tuple): month in a year, from 1 to 12
            week (tuple): week in a month, from 1 to 4
            day (tuple): day in a month, from 1 to 31
            weekday (tuple): weekday in a week, from 0 to 7. 0 and 7 both represent Sunday
            hour (tuple): hour in a day, from 0 to 24
            minute (tuple): minute in an hour, from 0 to 59

        Returns:
            list: a list of dictionarie(s) with form [{'Day':12, 'Month':3}, {}, etc]
        '''
        dic = {
            'Month': month,
            'Day': day,
            'Week': week,
            'Weekday': weekday,
            'Day': day,
            'Hour': hour,
            'Minute': minute
        }
        dic = {k: v for k, v in dic.items() if v != ()}
        grandList = []
        for k in dic:
            # e.g. 'Month'
            l = []
            for num in dic[k]:  # e.g. (q, 4, 6, 8)
                l.append({k: num})  # e.g. {'Month': 4}
            grandList.append(l)
        print(grandList)
        return (crossCombine(grandList))

    def genInterval(self,
                    month=(),
                    day=(),
                    week=(),
                    weekday=(),
                    hour=(),
                    minute=()):
        '''Generate list of config dictionarie(s) that represent a interval of time. Used to be passed into add() or remove().
        For example::

            genInterval(month=(1,4), week(1,4))
            # generate list contains from first to third week in from January to March

        Args:
            month (tuple): (start, end) month in a year, from 1 to 12
            week (tuple): (start, end) week in a month, from 1 to 4
            day (tuple): (start, end) day in a month, from 1 to 31
            weekday (tuple): (start, end) weekday in a week, from 0 to 7. 0 and 7 both represent Sunday
            hour (tuple): (start, end) hour in a day, from 0 to 24
            minute (tuple): (start, end) minute in an hour, from 0 to 59

        Returns:
            list: a list of dictionarie(s) with form [{'Day':12, 'Month':3}, {}, etc]
        '''
        dic = {
            'Month': month,
            'Day': day,
            'Week': week,
            'Weekday': weekday,
            'Day': day,
            'Hour': hour,
            'Minute': minute
        }
        dic = {k: v for k, v in dic.items() if v != ()}
        # e.g. dic: {'month': (1,5), 'day': (2,4)}
        grandList = []
        for k in dic:
            # e.g. k: 'month', dic[k]: (1,5)
            l = []
            # rangeTuple = (dic[k][0], dic[k][1] + 1)  # e.g. (1,6)
            rangeTuple = dic[k]
            for num in range(rangeTuple[0],
                             rangeTuple[1]):  # e.g. 1, 2, 3, 4, 5
                l.append({k: num})  # e.g. [{'month': 1}, {'month': 2}]
            grandList.append(l)  # e.g. [[list of month], [list of day]]
        print(grandList)
        # grandList: [[list of month], [list of day]]
        # l: [[a,a1,a2,...], [b,b1,b2,...]]
        # combineDict return: [{a,b}, {a,b1}, {a,b2}, {a1,b}, {a1,b1}, {a1, b2}, {a2,b}, {a2,b1}, {a2,b2}]
        return crossCombine(grandList)


class StartOnMount(BoolPair):
    '''StartOnMount config

    Example::

        config = StartOnMount()
    '''
    pass


class WatchPaths(OuterOFInnerPair):
    '''WatchPaths config

    Example::

        config = WatchPaths(['/path1', '/path2', '/path3'])
        config = WatchPaths('/path2')
        config = WatchPaths('/path1', '/path2', '/path3')
        config.remove('/path1')
        config.add('/path1')
    '''

    def __init__(self, *l):
        '''init

        Args
            *l: path you want to watch
        '''
        super().__init__(ArraySingle, StringSingle, l)


class QueueDirecotries(OuterOFInnerPair):
    '''QueueDirectories config

    Example::

        config = QueueDirectories(['/path1', '/path2', '/path3'])
        config = QueueDirectories('/path2')
        config = QueueDirectories('/path1', '/path2', '/path3')
        config.remove('/path1')
        config.add('/path1')
    '''

    def __init__(self, *l):
        '''init

        Args
            *l: path you want to watch
        '''
        super().__init__(ArraySingle, StringSingle, l)


# Keep Alive class in two branch classes and a factory function
class KeepAliveAlways(BoolPair):
    '''KeepAlive option'''

    def __init__(self):
        self.key = 'KeepAlive'
        self.setToTrue()


class KeepAliveDepends(OuterOFInnerPair):
    def __init__(self, *key):
        super().__init__(DictSingle, BoolPair, *key)
        self.key = 'KeepAlive'

    def addKey(self, key, *value):
        self._add([key(*value)], self.l)

    def removeKey(self, key, *value):
        self._remove([key(*value)], self.l)


def KeepAlive(branch='always', *key):
    '''KeepAlive config

    Example::

        config = KeepAlive('always') # keepAlive no matter what
        config2 = KeepAlive('depends', SuccessfulExit())
        config2.addKey(Crashed())
        config2.removeKey(Crashed())
        config2.addKey(OtherJobEnabled('some-job'))

    You can also use ``KeepAliveAlways()`` or ``KeepAliveDepends()``, ``KeepAlive()`` is just a helper function that returns either one of the two classes.

    Args:
        branch (str): indicates which version of ``KeepAlive`` you want, can be either 'always' or 'depends'.
        *key (str): If there is any key to be passed to depend version of ``KeepAlive``, put it in ``key``. Possible keys are ``SuccessfulExit()``, ``Crashed()``, ``OtherJobEnabled()``, ``AfterInitialDemand()`` and ``PathState()``.


    Raises:
        KeyError: if branch is not one of 'always' and 'depends'

    Returns:
        class: the actual class. Either ``KeepAliveAlways`` or ``KeepAliveDepends``.
    '''
    if branch == 'always':
        return KeepAliveAlways()
    elif branch == 'depends':
        return KeepAliveDepends(key)
    else:
        raise KeyError('branch only accept either \'always\' or \'depends\'')


class SuccessfulExit(BoolPair):
    '''SuccessfulExit option for KeepAlive'''
    pass


class Crashed(BoolPair):
    '''Crashed option for KeepAlive'''
    pass


class OtherJobEnabled(OuterOFInnerPair):
    '''OtherJobEnabled option for KeepAlive

    Example::

        OtherJobEnabled('some-job')
    '''

    def __init__(self, *key):
        '''init

        Args
            *l: job you want to refer to
        '''
        super().__init__(DictSingle, BoolPair, *key)


class AfterInitialDemand(OuterOFInnerPair):
    '''AfterInitialDemand option for KeepAlive'''

    def __init__(self, *key):
        '''init

        Args
            *l: job you want to refer to
        '''
        super().__init__(DictSingle, BoolPair, *key)


# MARK: add after initial demand
class PathState(OuterOFInnerPair):
    '''PathState option for KeepAlive'''

    def __init__(self, *key):
        '''init

        Args
            *l: path you want to refer to
        '''
        super().__init__(DictSingle, BoolPair, *key)


# KeepAlive ends


class UserName(SingleStringPair):
    '''UserName config

    Example::

        config = UserName('some-user')
        config.changeTo('some-other-user')
    '''
    pass


class GroupName(SingleStringPair):
    '''GroupName config

    Example::

        config = GroupName('some-group')
        config.changeTo('some-other-group')
    '''
    pass


class InitGroups(SingleStringPair):
    '''Label InitGroups

    Example::

        config = InitGroups('some-group')
        config.changeTo('some-other-group')
    '''
    pass


class Umask(SingleIntegerPair):
    '''Umask config

    Example::

        config = Label(0)
        config.changeTo(1)
    '''
    pass


class RootDirecotry(SingleStringPair):
    '''RootDirecotry config

    Example::

        config = RootDirecotry('some-dir')
        config.changeTo('some-other-dir')
    '''
    pass


class AbandonProcessGroup(BoolPair):
    '''AbandonProcessGroup config

    Example::

        config = AbandonProcessGroup()
    '''
    pass


class ExitTimeOut(SingleIntegerPair):
    '''ExitTimeOut config

    Example::

        config = Label(30)
        config.changeTo(60)
    '''
    pass


class Timeout(SingleIntegerPair):
    '''Timeout config

    Example::

        config = Timeout(30)
        config.changeTo(60)
    '''
    pass


class ThrottleInverval(SingleIntegerPair):
    '''ThrottleInverval config

    Example::

        config = Label(5)
        config.changeTo(10)
        KeepAlive('always', ThrottleInverval(5))

    '''
    pass


class LegacyTimers(BoolPair):
    '''LegacyTimers config

    Example::

        config = LegacyTimers()
    '''
    pass


class Nice(SingleIntegerPair):
    '''Nice config

    Example::

        config = Nice(-5)
        config.changeTo(20)
    '''
    pass
