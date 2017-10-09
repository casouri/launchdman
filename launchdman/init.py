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
        '''
        super().__init__()
        self.value = [Outer()]
        self.l = self.value[0].value
        self.Outer = Outer
        self.Inner = Inner
        self.add(l)

    def add(self, *l):
        for a in flatten(l):
            self._add([self.Inner(a)], self.l)

    def remove(self, *l):
        for a in flatten(l):
            self._remove([self.Inner(a)], self.l)


class BoolPair(Pair):
    '''
    A special type of pair that contains it's key and
    only one tag, usually </true> or </false>.
    At init, value will be set as true.
    '''

    def __init__(self, key=''):
        super().__init__(key)
        self.setToTrue()

    def setToTrue(self):
        '''
        This function sets the value of key true.
        '''
        self.value = [BoolSingle('true')]

    def setToFalse(self):
        '''
        Might be needed, set value to false
        '''
        self.value = [BoolSingle('false')]


class SingleDictPair(Pair):
    '''
    Pair that contains one DictSingle in its value
    '''

    def __init__(self, dic):
        super().__init__()
        self.value = [DictSingle()]
        self.d = self.value[0].value
        self.add(dic)

    def add(self, dic):
        for kw in dic:
            checkKey(kw, self.keyWord)
            self._add([Pair(kw, StringSingle(dic[kw]))], self.d)

    def remove(self, dic):
        for kw in dic:
            removePair = Pair(kw, dic[kw])
            self._remove([removePair])


class Label(SingleStringPair):
    pass


class Program(SingleStringPair):
    pass


class ProgramArguments(OuterOFInnerPair):
    def __init__(self, *l):
        super().__init__(ArraySingle, StringSingle, l)


class EnvironmentVariables(Pair):
    def __init__(self, path):
        super().__init__()
        self.changeTo(path)

    def changeTo(self, path):
        dictionary = DictSingle(Pair('PATH', StringSingle(path)))
        self.value = [dictionary]


class StandardInPath(SingleStringPair):
    pass


class StandardOutPath(SingleStringPair):
    pass


class StandardErrorPath(SingleStringPair):
    pass


class WorkingDirectory(SingleStringPair):
    pass


class SoftResourceLimit(SingleDictPair):
    keyWord = [
        'CPU', 'FileSize', 'NumberOfFiles', 'Core', 'Data', 'MemoryLock',
        'NumberOfProcesses', 'ResidentSetSize', 'Stack'
    ]


class HardResourceLimit(SingleDictPair):
    keyWord = [
        'CPU', 'FileSize', 'NumberOfFiles', 'Core', 'Data', 'MemoryLock',
        'NumberOfProcesses', 'ResidentSetSize', 'Stack'
    ]


class RunAtLoad(BoolPair):
    pass


class StartInterval(Pair):
    baseNumber = 1
    magnification = 1

    def __init__(self):
        super().__init__()

    def every(self, baseNumber):
        self.baseNumber = baseNumber
        return self

    def _update(self, baseNumber, magnification):
        interval = int(baseNumber * magnification)
        self.value = [IntegerSingle(interval)]

    @property
    def second(self):
        self.magnification = 1
        self._update(self.baseNumber, self.magnification)

    @property
    def minute(self):
        self.magnification = 60
        self._update(self.baseNumber, self.magnification)

    @property
    def hour(self):
        self.magnification = 3600
        self._update(self.baseNumber, self.magnification)

    @property
    def day(self):
        self.magnification = 86400
        self._update(self.baseNumber, self.magnification)

    @property
    def week(self):
        self.magnification = 345600
        self._update(self.baseNumber, self.magnification)


class StartCalendarInterval(Pair):
    keyWord = ['Month', 'Day', 'Weekday', 'Hour', 'Minute']

    def __init__(self, *dic):
        super().__init__()
        self.value = [ArraySingle()]
        self.l = self.value[0].value

    def add(self, *dic):
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
        dicList = list(flatten(dic))
        for d in dicList:
            di = []
            for k in d:
                # checkkey(k, self.keyword)
                di.append(Pair(k, IntegerSingle(d[k])))
            dictSingle = DictSingle(di)
            # append dict single to array single
            self._remove([dictSingle], self.l)

    def gen(self, month=0, day=0, week=0, weekday=0, hour=0, minute=0):
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
        '''
        e.g. month=(1, 4, 6, 8), day=tuple(range(1, 30, 2))
        Keep in mind that range(1, n) gives you (1, 2, ... , n-1)
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
        '''
        generate list of dict to passed to add.
        e.g. genInterval(month=(1,3), week(1,2))
        generate list contains from first to second week in from January to March
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
            rangeTuple = (dic[k][0], dic[k][1] + 1)  # e.g. (1,6)
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
    pass


class WatchPaths(OuterOFInnerPair):
    def __init__(self, *l):
        super().__init__(ArraySingle, StringSingle, l)


class QueueDirecotries(OuterOFInnerPair):
    def __init__(self, *l):
        super().__init__(ArraySingle, StringSingle, l)


# Keep Alive class in two branch classes and a factory function
class always(BoolPair):
    def __init__(self):
        self.key = 'KeepAlive'
        self.setToTrue()


class depends(OuterOFInnerPair):
    def __init__(self, *key):
        super().__init__(DictSingle, BoolPair, *key)
        self.key = 'KeepAlive'

    def addKey(self, key, *value):
        self._add([key(*value)], self.l)

    def removeKey(self, key, *value):
        self._remove([key(*value)], self.l)


def KeepAlive(KeepAliveBranch=always, *key):
    return KeepAliveBranch(*key)


class OtherJobEnabled(OuterOFInnerPair):
    def __init__(self, *key):
        super().__init__(DictSingle, BoolPair, *key)


class AfterInitialDemand(OuterOFInnerPair):
    def __init__(self, *key):
        super().__init__(DictSingle, BoolPair, *key)


# MARK: add after initial demand
class PathState(OuterOFInnerPair):
    def __init__(self, *key):
        super().__init__(DictSingle, BoolPair, *key)


# KeepAlive ends


class UserName(SingleStringPair):
    pass


class GroupName(SingleStringPair):
    pass


class InitGroups(SingleStringPair):
    pass


class Umask(SingleIntegerPair):
    pass


class RootDirecotry(SingleStringPair):
    pass


class AbandonProcessGroup(BoolPair):
    pass


class ExitTimeOut(SingleIntegerPair):
    pass


class Timeout(SingleIntegerPair):
    pass


class ThrottleInverval(SingleIntegerPair):
    pass


class LegacyTimers(BoolPair):
    pass


class Nice(SingleIntegerPair):
    pass
