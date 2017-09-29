import textwrap
import collections


def indent(text, amount, ch=' '):
    return textwrap.indent(text, amount * ch)


def flatten(l):
    for el in l:
        if isinstance(
                el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


# def makeReferenceList(originList):
#     referenceList = []
#     for i in originList:
#         referenceList.append(i)
#     return referenceList


class SingleBool():
    '''
    A type of Single that only have a single tag.
    Usually indicate true of false.
    '''
    scalar = ''

    def __init__(self, scalar):
        self.scalar = scalar

    def printMe(self, scalar):
        text = '</{scalar}>\n'.format(scalar=scalar)
        return text


class Single():
    '''
    A type of structure that only have a tag and it's values.
    At init, tag and value will be set to empty.
    '''
    tag = ''
    value = []

    def __init__(self, tag, *value):
        self.tag = tag
        self.value = list(flatten(value))

    def printMe(self, tag, value):
        if len(value) == 0:
            return ''
        elif len(value) == 1:
            text = '<{tag}>{value}</{tag}>\n'.format(tag=tag, value=value[0])
            return text
        else:
            valueText = ''
            for single in value:
                valueText += single.printMe(single.tag, single.value)
            valueText = indent(valueText, 4)
            text = '<{tag}>\n'.format(
                tag=tag) + valueText + '</{tag}>\n'.format(tag=tag)
            return text


class TypedSingle(Single):
    '''
    A little sugar so that you don't need to
    type the tag every time creating a single
    '''

    def __init__(self, *value):
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


class Pair():
    '''
    A type of structure that have <key>Key</key> and it's value.
    By default, value is set to empty.
    Its value should contain only one single.
    If not provide in init parameter, key is set to subclass name in init.
    Init also accept value in combination of strings
    and lists of strings.

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
                # may be remove the loop
                # single = value[0]
                if isinstance(single, Single):
                    valueText += single.printMe(single.tag, single.value)
                elif isinstance(single, SingleBool):
                    valueText += single.printMe(single.scalar)

        text += valueText
        return text

    def clear(self):
        self.value = []


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


class SingleStringPairTemplate(Pair):
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


class ArrayPairTemplate(Pair):
    def __init__(self, value):
        super().__init__()
        self.add(value)

    def update(self, *value):
        self.value.append(list(flatten(value)))

    def add(self, *value):
        arraySingle = ArraySingle(value)


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


class StartInterval(Pair):
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
