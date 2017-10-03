import textwrap
from collections import Iterable


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
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


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


# def makeReferenceList(originList):
#     referenceList = []
#     for i in originList:
#         referenceList.append(i)
#     return referenceList


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
        self.printMe(self.tag, self.value)

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
        takes in self.value as l
        '''
        resultList = []
        for element in selfValue:
            if isinstance(element, Single):
                resultList += element.findAll()
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


class BoolSingle(Single):
    '''
    A type of Single that only have a single tag.
    The only difference is it prints differently.
    Usually indicate true of false.
    '''

    def __init__(self, boolValue):
        self.value = [boolValue]

    def printMe(self, selfTag='', selfValue='true'):
        text = '</{value}>\n'.format(value=selfValue)
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


class CoverPair(Pair):
    '''
    pair that have a array or dict as value.
    Then it make sense to let add and remove act on that array/dict's value
    instead of instance.value.
    Its value should contain only one single.
    '''

    # def add(self, *value):
    #     '''
    #     add to self.value.value
    #     '''
    #     flattenedValueList = list(flatten(value))
    #     super()._add(flattenedValueList, self.value[0].value)
    #     return (flattenedValueList)

    # def remove(self, *l):
    #     '''
    #     remove from self.value.value
    #     '''
    #     removeList = list(flatten(l))
    #     super()._remove(removeList, self.value[0].value)


class SingleStringPair(Pair):
    def __init__(self, string):
        super().__init__()
        self.changeTo(string)

    def changeTo(self, newString):
        '''change string single to newString'''
        stringSingle = StringSingle(newString)
        self.value = [stringSingle]


class BoolPair(Pair):
    '''
    A special type of pair that contains it's key and
    only one tag, usually </true> or </false>.
    At init, value will be set as true.
    '''

    def __init__(self):
        super().__init__()
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
        self.dicValue = self.value[0].value
        self.add(dic)

    def add(self, dic):
        for kw in dic:
            # if kw not in self.keyWord:
            #     raise AttributeError('key word "{}" not valid'.format(kw))
            checkKey(kw, self.keyWord)
            self.dicValue.append(Pair(kw, StringSingle(dic[kw])))

    def remove(self, dic):
        for kw in dic:
            removePair = Pair(kw, dic[kw])
            self._remove([removePair])


class Label(SingleStringPair):
    pass


class Program(SingleStringPair):
    pass


class ProgramArguments(Pair):
    '''
    takes a list of strings or a single string
    '''

    def __init__(self, *l):
        super().__init__()
        stringList = []
        for string in list(flatten(l)):
            stringSingle = StringSingle(string)
            stringList.append(stringSingle)
        arraySingle = ArraySingle(stringList)
        self.value = [arraySingle]

    def add(self, argument):
        self.value[0].add(StringSingle(argument))


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
        self.l = self.value[0]

    def add(self, *dic):
        dicList = list(flatten(dic))
        for d in dicList:
            checkKey(d, self.keyWord)
            self.l.append(Pair(d, dicList[d]))

    def remove(self, *dic):
        dicList = list(flatten(dic))
        for d in dicList:
            self._remove([Pair(d, dicList[d])], self.l)

    def gen(self, month=0, day=0, week=0, weekday=0, hour=0, minute=0):
        dic = {
            'Month': month,
            'Day': day,
            'Week': week,
            'Weekday': weekday,
            'Day': day,
            'Minute': minute
        }
        dic = {k: v for k, v in dic.iteritems() if v != 0}
        self.add(dic)

    #MARK: bookmark
    def rm(self, month=0, day=0, week=0, weekday=0, hour=0, minute=0):
        dic = {
            'Month': month,
            'Day': day,
            'Week': week,
            'Weekday': weekday,
            'Day': day,
            'Minute': minute
        }
        dic = {k: v for k, v in dic.iteritems() if v != 0}
        self.add(dic)


class StartOnMount():
    pass


class WatchPath():
    pass


class QueueDirecotries():
    pass


class KeepAlive():
    pass


class UserName():
    pass


class GroupName():
    pass


class InitGroups():
    pass


class Umask():
    def __init__(self):
        pass

    def update(self):
        pass


class RootDirecotry():
    def __init__(self):
        pass

    def update(self):
        pass


class AbandonProcessGroup():
    def __init__(self):
        pass

    def update(self):
        pass


class ExitTimeOut():
    def __init__(self):
        pass

    def update(self):
        pass


class Timeout():
    def __init__(self):
        pass

    def update(self):
        pass


class ThrottleInverval():
    def __init__(self):
        pass

    def update(self):
        pass


class LegacyTimers():
    def __init__(self):
        pass

    def update(self):
        pass


class Nice():
    def __init__(self):
        pass

    def update(self):
        pass


if __name__ == '__main__':
    # innerSingle1 = Single('inner1', 'aaaaaaaaaaaaa')
    # innerSingle2 = Single('inner2', 'bbbbbbbbbbbbb')
    # single1 = Single('single tag1', innerSingle1, innerSingle2)
    # single2 = Single('single tag2', innerSingle1, innerSingle2)
    # singleSingle = Single('singleSingle', 'something')
    # pair1 = Pair('my key', single1, single2)
    # pair2 = Pair('mey key', singleSingle)
    # print(pair2.printMe(pair2.key, pair2.value))

    # schedule = StartInterval()
    # schedule.every(5).day
    # schedule.every(10).minute
    schedule = RunAtLoad()
    print(schedule.key)
    print(schedule.printMe(schedule.key, schedule.value))
