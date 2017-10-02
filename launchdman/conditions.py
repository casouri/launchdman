import textwrap
from collections import Iterable


def indent(text, amount, ch=' '):
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
        raise AttributeError(
            'Not enough super class. Are you sure this is either a instance of Single or Pair?'
        )
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


class SingleBool(Single):
    '''
    A type of Single that only have a single tag.
    The only difference is it prints differently.
    Usually indicate true of false.
    '''
    scalar = ''

    def __init__(self, value):
        self.value = value

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
    '''
    No difference from array but with a tag named dict
    and should contain only pair instance.
    '''
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
                    # MARK: working: should add a else statement

        text += valueText
        return text


class CoverPair(Pair):
    '''
    pair that have a array or dict as value.
    Then it make sense to let add and remove act on that array/dict's value
    instead of instance.value.
    only difference is that add and remove action directly
    on Pair's instance.value.value, instead of Pair's instance.value
    Its value should contain only one single.
    '''

    def add(self, *value):
        '''
        add to self.value.value
        '''
        flattenedValueList = list(flatten(value))
        super()._add(flattenedValueList, self.value[0].value)
        return (flattenedValueList)

    def remove(self, *l):
        '''
        remove from self.value.value
        '''
        removeList = list(flatten(l))
        super()._remove(removeList, self.value[0].value)


class SingleValuePair(Pair):
    '''
    Pair that only contain a key and a single which contain only one value.
    subclass have to implement changeTo method
    '''

    def __init__(self):
        super().__init__()

    def changeTo(self, value):
        raise AttributeError(
            'sub-class of "SingleValuePair" class should implement different "changeTo" method'
        )

    def add(self):
        '''no add method'''
        raise AttributeError('"SingleStringPair" class has no method "add"')

    def remove(self):
        '''no remove method'''
        raise AttributeError('"SingleStringPair" class has no method "remove"')


class BoolPairTemplate(Pair):
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
        trueBool = SingleBool('true')
        self.value = [trueBool]


class Label(SingleValuePair):
    def changeTo(self, label):
        '''change string single to label'''
        stringSingle = StringSingle(label)
        self.value = [stringSingle]


class Program(SingleValuePair):
    def changeTo(self, label):
        '''change string single to label'''
        stringSingle = StringSingle(label)
        self.value = [stringSingle]


class ProgramArguments(CoverPair):
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


class EnvironmentVariables(SingleValuePair):
    def __init__(self, path):
        super().__init__()
        self.changeTo(path)

    def changeTo(self, path):
        dictionary = DictSingle(Pair('PATH', StringSingle(path)))
        self.value = [dictionary]


class StandardInPath():
    def update(self):
        pass


class StandardOutPath():
    def update(self):
        pass


class StandardErrorPath():
    def update(self):
        pass


class WorkingDirectory():
    def update(self):
        pass


class SoftResourceLimit():
    def __init__(self):
        pass

    def update(self):
        pass


class HardResourceLimit():
    def __init__(self):
        pass

    def update(self):
        pass


class RunAtLoad(BoolPairTemplate):
    pass


class StartInterval(CoverPair):
    baseNumber = 1
    magnification = 1
    key = 'StartInterval'

    def __init__(self):
        pass

    def every(self, baseNumber):
        self.baseNumber = baseNumber
        return self

    def _update(self, baseNumber, magnification):
        schedule = baseNumber * magnification
        integerSingle = Single('integer', schedule)
        if len(self.value) != 0:
            self.value = []
        self.value.append(integerSingle)

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


class StartCalendarInterval():
    def __init__(self):
        pass


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
