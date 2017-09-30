import textwrap
from collections import namedtuple, Iterable


def indent(text, amount, ch=' '):
    return textwrap.indent(text, amount * ch)


def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def removeeverything(toBeRemoved, l):
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
        return set(self.findAll()) == set(other.findAll())

    def __init__(self, tag, *value):
        self.tag = tag
        self.value = list(flatten(value))

    def printMe(self, tag, value):
        if len(value) == 0:
            return ''
        # if value have only one element and it is not another single
        # print differently
        elif len(value) == 1 and not isinstance(value[0], Single):
            text = '<{tag}>{value}</{tag}>\n'.format(tag=tag, value=value[0])
            return text
        else:
            valueText = ''
            for single in value:
                # if the element is another single
                # or merely an object
                # both possibility should not happen in the same time
                # if so, user is not doing the right thing
                if isinstance(single, Single):
                    # ask that single to print itself
                    valueText += single.printMe(single.tag, single.value)
                else:
                    # simply print that element
                    valueText += str(single) + '\n'
            valueText = indent(valueText, 4)
            text = '<{tag}>\n'.format(
                tag=tag) + valueText + '</{tag}>\n'.format(tag=tag)
            return text

    def findAll(self):
        resultList = []
        for element in self.value:
            if isinstance(element, Single):
                resultList += element.findAll()
            else:
                resultList.append(element)
        return resultList

    def findAllSingle(self):
        resultList = []
        for element in self.value:
            if isinstance(element, Single):
                resultList.append(element)
                resultList += element.findAllSingle()
        return resultList

    def add(self, *value):
        '''
        Subclass are responsible of creating whatever single instance it need
        from its add(*value). And make a list and pass the list to add().
        '''
        flattenedValueList = list(flatten(value))
        self.value += flattenedValueList
        return (flattenedValueList)

    def remove(self, *l):
        '''
        only looks inside current instance's value, not recursive.
        There is no need for a recursive one anyway.
        '''
        removeList = list(flatten(l))
        for removeValue in removeList:
            removeeverything(removeValue, self.value)

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

    def printMe(self, tag='', value='true'):
        text = '</{value}>\n'.format(value=value)
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

    def printMe(self, key, value):
        text = '<key>{keyName}</key>\n'.format(keyName=key)

        if len(value) == 0:
            return ''
        else:
            valueText = ''
            for single in value:
                if isinstance(single, Single):
                    valueText += single.printMe(single.tag, single.value)
                elif isinstance(single, SingleBool):
                    valueText += single.printMe(single.scalar)

        text += valueText
        return text


class TopLevelPair(Pair):
    '''
    only difference is that add and remove action directly
    on Pair's instance.value, instead of Pair's instance
    Its value should contain only one single.
    If not provide in init parameter, key is set to subclass name in init.
    Init also accept value in combination of strings
    and lists of strings.
    '''
    pass


class BoolPairTemplate(TopLevelPair):
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


class SingleStringPairTemplate(TopLevelPair):
    '''
    Pair that only contain a key and a string single.
    '''

    def __init__(self, label):
        super().__init__()
        self.changeTo(label)

    def update(self, single):
        self.clear()
        self.value.append(single)

    def changeTo(self, label):
        stringSingle = StringSingle(label)
        self.update(stringSingle)


class ArrayPairTemplate(TopLevelPair):
    '''
    The type of Pair that contains a array single
    '''

    def __init__(self, value):
        super().__init__()
        self.add(value)

    def update(self, *value):
        self.value.append(list(flatten(value)))

    def make(self, *value):
        arraySingle = ArraySingle(value)
        return arraySingle

    def add(self, single):
        for valueElement in self.value:
            valueElement.add(single)
        self.value.append(ArraySingle)


class Label(SingleStringPairTemplate):
    pass


class Program(SingleStringPairTemplate):
    pass


class ProgramArguments():
    def update(self):
        pass


class EnvironmentVariables():
    def update(self):
        pass


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


class StartInterval(TopLevelPair):
    baseNumber = 1
    magnification = 1
    key = 'StartInterval'

    def __init__(self):
        pass

    def every(self, baseNumber):
        self.baseNumber = baseNumber
        return self

    def update(self, baseNumber, magnification):
        schedule = baseNumber * magnification
        integerSingle = Single('integer', schedule)
        if len(self.value) != 0:
            self.value = []
        self.value.append(integerSingle)

    @property
    def second(self):
        self.magnification = 1
        self.update(self.baseNumber, self.magnification)

    @property
    def minute(self):
        self.magnification = 60
        self.update(self.baseNumber, self.magnification)

    @property
    def hour(self):
        self.magnification = 3600
        self.update(self.baseNumber, self.magnification)

    @property
    def day(self):
        self.magnification = 86400
        self.update(self.baseNumber, self.magnification)

    @property
    def week(self):
        self.magnification = 345600
        self.update(self.baseNumber, self.magnification)


class StartCalendarInterval():
    def __init__(self):
        pass

    def update(self):
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
