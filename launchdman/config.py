import textwrap
from collections import Iterable
from pathlib import Path


def checkKey(key, keyList):
    if key not in keyList:
        raise AttributeError('"{}" is not a valid key'.format(key))


def indent(text, amount, ch=' '):
    '''take test and indent every line by amount characters

    :param text: text to be indented
    :type text: str
    :param amount: number of times indent character is repeated
    :type amount: int
    :param ch: the indent character, default as space
    :type ch: str
    :returns: a indented string
    :rtype: str

    '''
    return textwrap.indent(text, amount * ch)


def flatten(l):
    for el in l:
        # I don;t want dict to be flattened
        if isinstance(el, Iterable) and not isinstance(
                el, (str, bytes)) and not isinstance(el, dict):
            yield from flatten(el)
        else:
            yield el


def crossCombine(l):
    '''
    e.g.: l: [[{'month': 1}, {'month': 2}], [{'day': 2}, {'day': 3}, {'day': 4}]]
          l: [[dic of month], [dict of day]]
          l: [[a,a1,a2,...], [b,b1,b2,...]]
    return: [[a,b], [a,b1], [a,b2], [a1,b], [a1,b1], [a1, b2], [a2,b], [a2,b1], [a2,b2]]

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
    if not isinstance(a1, list):
        a1 = [a1]
    if not isinstance(a2, list):
        a2 = [a2]
    return a1 + a2


def combinteDict(d, d1):
    return {**d, **d1}


def ancestor(obj):
    return list(obj.__class__.__mro__)[-2]


def ancestorJr(obj):
    return list(obj.__class__.__mro__)[-3]


def singleOrPair(obj):
    if len(list(obj.__class__.__mro__)) <= 2:
        return 'neither'
    else:
        # Pair check comes first for Pair is a subclass of Single
        if ancestorJr(obj) is Pair:
            return 'Pair'
        elif ancestor(obj) is Single:
            return 'Single'


def removeEverything(toBeRemoved, l):
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
    At init, tag and value will be set to empty.
    All subclass must implement printMe(tag, value)
    '''
    tag = ''
    value = []

    def __eq__(self, other):
        # return self.printMe(self.tag, self.value) == other.printMe(
        #     other.tag, other.value)
        return set(self.findAll(self.value)) == set(other.findAll(other.value))

    def __init__(self, tag, *value):
        self.tag = tag
        self.value = list(flatten(value))

    def parse(self):
        return self.printMe(self.tag, self.value)

    def printMe(self, selfTag, selfValue):
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
        '''
        Looks for all the non single values
        returns a list of them
        '''
        resultList = []
        for element in selfValue:
            if isinstance(element, Single):
                resultList += element.findAll(element.value)
            else:
                resultList.append(element)
        return resultList

    def findAllSingle(self, selfValue):
        '''
        takes in self.value as value
        '''
        resultList = []
        for element in selfValue:
            if isinstance(element, Single):
                resultList.append(element)
                resultList += element.findAllSingle()
        return resultList

    def _add(self, value, selfValue):
        '''
        Subclass are responsible of creating whatever single instance it need
        from its add(*value). And make a list and pass the list to add().
        '''
        selfValue += value
        return (value)

    def add(self, *value):
        '''
        Subclass are responsible of creating whatever single instance it need
        from its add(*value).
        This is a public mask of _add.
        '''
        flattenedValueList = list(flatten(value))
        return self._add(flattenedValueList, self.value)

    def _remove(self, removeList, selfValue):
        '''
        only looks inside current instance's value, not recursive.
        There is no need for a recursive one anyway.
        '''
        for removeValue in removeList:
            print(removeValue, removeList)
            # if removeValue equal to selfValue, remove
            removeEverything(removeValue, selfValue)

    def remove(self, *l):
        '''
        only looks inside current instance's value, not recursive.
        There is no need for a recursive one anyway.
        public mask of _remove
        '''
        removeList = list(flatten(l))
        self._remove(removeList, self.value)

    def clear(self):
        self.value = []


class Job(Single):
    def __init__(self, path):
        self.me = Path(path)
        self.tag = 'dict'
        self.value = []

    def write(self):
        with open(self.me, 'w') as f:
            f.write(self.printMe(self.tag, self.value))

    def printMe(self, selfTag, selfValue):
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
    '''
    A type of Single that only have a single tag.
    The only difference is it prints differently.
    Usually indicate true of false.
    '''

    def __init__(self, boolValue):
        self.value = [boolValue]

    def printMe(self, selfTag='', selfValue='true'):
        text = '<{value}/>\n'.format(value=selfValue[0])
        return text


class TypedSingle(Single):
    '''
    A little sugar so that you don't need to
    type the tag every time creating a single
    '''

    def __init__(self, *value):
        '''
        eg. The tag of stringSingle will be string
        '''
        tag = self.__class__.__name__.replace('Single', '').lower()
        super().__init__(tag, value)


class StringSingle(TypedSingle):
    pass


class ArraySingle(TypedSingle):
    pass


class DictSingle(TypedSingle):
    pass


class IntegerSingle(TypedSingle):
    pass


class Pair(Single):
    '''
    A type of structure that have <key>Key</key> and it's value.
    By default, value is set to empty.

    '''
    key = ''
    value = []

    def __init__(self, key='', *value):
        if key == '':
            self.key = self.__class__.__name__
        else:
            self.key = key
        if len(value) != 0:
            self.value = list(flatten(value))

    def parse(self):
        return self.printMe(self.key, self.value)

    def printMe(self, selfKey, selfValue):
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
    def __init__(self, string):
        super().__init__()
        self.changeTo(string)

    def changeTo(self, newString):
        '''change string single to newString'''
        self.value = [StringSingle(newString)]


class SingleIntegerPair(Pair):
    def __init__(self, string):
        super().__init__()
        self.changeTo(string)

    def changeTo(self, newInt):
        '''change string single to newString'''
        self.value = [IntegerSingle(newInt)]


class OuterOFInnerPair(Pair):
    '''
    e.g.: array of string, dict of pair, array of bool
    Outer: ArraySingle, DictSingle
    Inner: Pair, StringSingle, IntegerSingle, BoolPair
    key is set to subclass name
    '''

    def __init__(self, Outer, Inner, *l):
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
